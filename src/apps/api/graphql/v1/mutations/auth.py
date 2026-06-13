import graphene
import graphql_jwt
from graphql_jwt.shortcuts import get_token, create_refresh_token

from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q
from apps.api.graphql.v1.types.auth import UserType
from apps.business.models import Business, Membership
from apps.account.models import User, OTP
from apps.api.helper import check_sms_available
from apps.account.tasks import send_sms_task

class RegisterUser(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=False)
        phone_number = graphene.String(required=True)
        password = graphene.String(required=True)
        full_name = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, full_name, password, phone_number, business_id=None):
        if len(password) < 8:
            return RegisterUser(
                success=False,
                message="Password must be at least 8 characters long"
            )

        # Agar business_id berilgan bo'lsa — tekshiramiz
        user_type = User.UserType.DASHBOARD
        if business_id:
            business = Business.objects.filter(
                Q(hash_id=business_id) | Q(tg_hash_id=business_id)
            ).first()
            if not business:
                return RegisterUser(
                    success=False,
                    message="Business not found"
                )

            business_id = business.id
            user_type = User.UserType.STORE
        else:
            business_id = 0  # dashboard uchun

        # Tekshir: shu biznes ichida phone number mavjudmi
        existing_user = User.objects.filter(
            business_id=business_id,
            phone_number=phone_number
        ).first()

        if existing_user:
            if not existing_user.is_active:
                existing_user.full_name = full_name
                existing_user.user_type = user_type
                existing_user.set_password(password)
                existing_user.save()
                return RegisterUser(
                    user=existing_user,
                    success=True,
                    message="User registered successfully. Please verify your account."
                )
            else:
                return RegisterUser(
                    success=False,
                    message="User with this phone number already exists and is active"
                )
        
        # Yangi user yaratish
        user = User.objects.create_user(
            phone_number=phone_number,
            full_name=full_name,
            business_id=business_id,
            user_type=user_type,
            password=password
        )

        return RegisterUser(
            user=user,
            success=True,
            message="User registered successfully. Please verify your account."
        )
        
class UpdateUser(graphene.Mutation):
    class Arguments:
        full_name = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, full_name):
        user = info.context.user

        try:
            user.full_name = full_name
            user.save()

            return UpdateUser(user=user, success=True, message="User updated successfully.")
        except Exception as e:
            return UpdateUser(success=False, message=str(e))

class LoginUser(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=False)
        email = graphene.String()
        phone_number = graphene.String() # 
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    token = graphene.String()
    access_token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, phone_number, password, email=None, business_id=None):
        try:
            if business_id:
                business = Business.objects.filter(
                    Q(hash_id=business_id) | Q(tg_hash_id=business_id)
                ).first()            
                if not business:
                    return LoginUser(success=False, message="Business not found.")
                business_id = business.id
            else:
                business_id = 0  # Dashboard user uchun default

            try:
                user = User.objects.get(phone_number=phone_number, business_id=business_id)
            except User.DoesNotExist:
                return LoginUser(success=False, message="Account not found. Please register first.")

            if not user.check_password(password):
                return LoginUser(success=False, message="Incorrect password")

            if not user.is_active:
                return LoginUser(success=False, message="This account is inactive. Please verify your account first.")

            if not user.is_phone_verified:
                return LoginUser(success=False, message="Phone number is not verified. Please verify it first.")

            access_token = get_token(user)
            refresh_token = create_refresh_token(user)

            return LoginUser(
                user=user,
                success=True,
                message="Login successful",
                token=access_token,
                access_token=access_token,
                refresh_token=refresh_token
            )

        except Exception as e:
            return LoginUser(success=False, message="An unexpected error occurred.")

class VerifyOTP(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=False)
        phone_number = graphene.String(required=True)
        otp_code = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    access_token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, otp_code, phone_number, business_id=None):
        try:
            if business_id:
                business = Business.objects.filter(
                    Q(hash_id=business_id) | Q(tg_hash_id=business_id)
                ).first()
                if not business:
                    return VerifyOTP(success=False, message="Business not found.")
                business_id = business.id
            else:
                business_id = 0

            user = User.objects.get(phone_number=phone_number, business_id=business_id)
            
            if user.is_active:
                return VerifyOTP(success=False, message="This account is already active")
            
            # Get the latest OTP for this user
            try:
                otp = OTP.objects.filter(user=user, type=OTP.OtpType.ACTIVATION).latest('created_at')
            except OTP.DoesNotExist:
                return VerifyOTP(success=False, message="No OTP found")

            if otp.is_expired():
                return VerifyOTP(success=False, message="OTP expired")

            if otp.code != otp_code:
                return VerifyOTP(success=False, message="Invalid OTP")

            
            user.is_phone_verified = True
            user.is_active = True
            user.save()

            if business_id != 0:
                Membership.objects.get_or_create(
                    user=user,
                    business=business,
                )

            # Generate JWT token after successful verification
            access_token = get_token(user)
            refresh_token = create_refresh_token(user)

            return VerifyOTP(
                success=True, 
                message="Account activated successfully", 
                access_token=access_token,
                refresh_token=refresh_token
            )
        
        except User.DoesNotExist:
            return VerifyOTP(success=False, message="Account not found. Please register first.")
        except Exception as e:
            return VerifyOTP(success=False, message=str(e))

class RequestOTP(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=True)
        phone_number = graphene.String(required=True)
        purpose = graphene.String(required=True)  # 'activation', 'reset_password'

    success = graphene.Boolean()
    message = graphene.String()
    cooldown = graphene.Int()

    def mutate(self, info, phone_number, purpose, business_id):
        if purpose not in OTP.OtpType.values:
            return RequestOTP(
                success=False,
                message=f"Invalid purpose. Must be one of: {', '.join(OTP.OtpType.values)}"
            )
        
        business = Business.objects.filter(
            Q(hash_id=business_id) | Q(tg_hash_id=business_id)
        ).first()           
        if not business:
            return RequestOTP(success=False, message="Business not found.")
        business_id = business.id
        try:
            user = User.objects.get(phone_number=phone_number, business_id=business_id)
        except User.DoesNotExist:
            return RequestOTP(
                success=False,
                message="Account not found. Please register first."
            )

        if purpose == OTP.OtpType.ACTIVATION and user.is_active:
            return RequestOTP(
                success=False,
                message="Account is already active"
            )
        
        if purpose == OTP.OtpType.PASSWORD_RESET and not user.is_active:
            return RequestOTP(
                success=False,
                message="This account is inactive, Please verify your account first"
            )


        otp = OTP.objects.filter(user=user, type=purpose).first()
                
        if otp:        # Check if existing OTP is still valid
            if not otp.is_expired():
                remaining = OTP.EXPIRY_SECONDS - (now() - otp.created_at).total_seconds()
                minutes = int(remaining) // 60
                seconds = int(remaining) % 60
                return RequestOTP(
                    success=False,
                    message=f"Previous code is still valid for {minutes}m {seconds}s",
                    cooldown=int(remaining)
                )
            
            # Check cooldown time
            try:
                otp.can_send_new_code()
            except ValueError as e:
                return RequestOTP(
                    success=False,
                    message=str(e),
                    cooldown=otp.get_cooldown_time()
                )
            ok, source = check_sms_available(business, phone_number)
            if not ok:
                return RequestOTP(
                    success=False,
                    message="SMS yuborish uchun limit yoki balans yetarli emas"
                )
            # Update existing OTP
            otp.code = OTP.generate_code()
            otp.created_at = now()
            otp.save()
        else:
            ok, source = check_sms_available(business, phone_number)
            if not ok:
                return RequestOTP(
                    success=False,
                    message="SMS yuborish uchun limit yoki balans yetarli emas"
                )
            otp = OTP.objects.create(
                user=user,
                type=purpose,
                code=OTP.generate_code()
            )

        # Send OTP
        try:
            send_sms_task.delay(
                phone_number=phone_number,
                business_name=business.name,
                message_type="ACTIVATION" if purpose == OTP.OtpType.ACTIVATION else "FORGOT_PASSWORD",
                code=otp.code,
                business_id=business.id,
                source=source,
                otp_id=otp.id
            )

            return RequestOTP(
                success=True,
                message=f"{purpose.replace('_', ' ').title()} code sent successfully",
                cooldown=otp.get_cooldown_time()
            )
        except ValueError as e:
            return RequestOTP(
                success=False,
                message=str(e),
                cooldown=otp.get_cooldown_time()
            )

        except Exception as e:
            return RequestOTP(
                success=False,
                message="OTP yuborishda ichki xatolik yuz berdi"

            )


class ResetPassword(graphene.Mutation):
    class Arguments:
        business_id = graphene.String(required=False)
        phone_number = graphene.String(required=True)
        otp_code = graphene.String(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, otp_code, new_password, phone_number, business_id=None):
        try:
            if business_id:
                business = Business.objects.filter(
                    Q(hash_id=business_id) | Q(tg_hash_id=business_id)
                ).first()               
                if not business:
                    return ResetPassword(success=False, message="Business not found.")
                business_id = business.id
            else:
                business_id = 0
            
            user = User.objects.get(phone_number=phone_number, business_id=business_id)
            
            if not user:
                return ResetPassword(success=False, message="Account not found. Please register first.")
            
            if not user.is_active:
                return ResetPassword(success=False, message="This account is inactive, Please verify your account first")
            
            try:
                otp = OTP.objects.filter(user=user, type=OTP.OtpType.PASSWORD_RESET).first()
            except OTP.DoesNotExist:
                return ResetPassword(success=False, message="No OTP found")

            if otp.is_expired():
                return ResetPassword(success=False, message="OTP expired")

            if otp.code != otp_code:
                return ResetPassword(success=False, message="Invalid OTP")

            otp.created_at = now() - timedelta(seconds=OTP.EXPIRY_SECONDS)  # Mark as expired
            otp.save()
            
            # Set new password
            user.set_password(new_password)
            user.save() 

            return ResetPassword(success=True, message="Password reset successful")
        except Exception as e:
            return ResetPassword(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    update_user = UpdateUser.Field()
    verify_otp = VerifyOTP.Field()
    request_otp = RequestOTP.Field()
    reset_password = ResetPassword.Field()

    login_user = LoginUser.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
