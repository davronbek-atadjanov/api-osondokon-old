from django.db import models
from django.utils import timezone

'''
model Business {
  name          String
  subscription  Subscription?
  account       Decimal         @default(0.0)
  currency      Currency        @relation(fields: [currencyId], references: [id])
  currencyId    Int
  languages     String[]
  is_finished   Boolean         @default(false)
  step          Int             @default(0)
  platforms     Platform[]
  business_type BusinessType
  is_otp_allowed Boolean         @default(false)
  permissions   Permission[]
  is_admin      Boolean         @default(false)
  createdAt     DateTime        @default(now())
  updatedAt     DateTime        @updatedAt
  products      Product[]
  categories    Category[]
  locations     Location[]
  banners       Banner[]
  fields        BusinessField[]
  paymentTypes  PaymentType[]
  deliveryMethods DeliveryMethod[]
}
'''

class Business(models.Model):
    name = models.CharField(max_length=255)

    hash_id = models.CharField(max_length=64, blank=True, null=True)
    tg_hash_id = models.CharField(max_length=64, blank=True, null=True)

    favicon = models.CharField(max_length=4096, blank=True, null=True)
    logo = models.CharField(max_length=4096, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    step = models.CharField(max_length=255, blank=True, null=True)
    is_finished = models.BooleanField(default=False)
    multi_operator_mode = models.BooleanField(default=False)
    otp_enabled = models.BooleanField(default=False)

    account = models.IntegerField(default=0)
    currency = models.CharField(max_length=255, blank=True)
    

    languages = models.JSONField(default=dict, blank=True)
    social_info = models.JSONField(default=dict, blank=True)
    working_days = models.JSONField(default=dict, blank=True)
    payment_methods = models.JSONField(default=dict, blank=True)
    platforms = models.JSONField(default=dict, blank=True)

    fields = models.ManyToManyField('business.BusinessField', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def active_subscription(self):
        """Get the currently active subscription"""
        return self.subscription_set.filter(
            start_date__lte=timezone.now().date(),
            end_date__gte=timezone.now().date()
        ).first() or self.subscription_set.filter(
            start_date__lte=timezone.now().date(),
            end_date__isnull=True
        ).first()
    
    @property
    def plan(self):
        """Get the current plan tier (basic/pro/enterprise)"""
        sub = self.active_subscription
        return sub.subscription_type if sub else None

    @property
    def plan_expiry(self):
        """
        Returns the furthest end_date from active and future subscriptions.
        Useful when user stacked multiple future subscriptions.
        """
        subs = self.subscription_set.filter(
            start_date__gte=timezone.now().date()
        ).order_by('-end_date')

        if not subs.exists():
            # fallback to current active sub
            if self.active_subscription and self.active_subscription.end_date:
                return self.active_subscription.end_date
            return None

        latest = subs.first()
        return latest.end_date

    
    @property
    def upcoming_subscriptions(self):
        """Get subscriptions that will activate in the future"""
        return self.subscription_set.filter(
            start_date__gt=timezone.now().date()
        ).order_by('start_date')
    
    @property
    def has_active_subscription(self):
        """Check if business has any active subscription"""
        return self.active_subscription is not None

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'businesses'
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'

class Branch(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    latitude = models.CharField(max_length=255, default="")
    longitude = models.CharField(max_length=255, default="")

    is_main_branch = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)

    delivery_enabled = models.BooleanField(default=False)
    pickup_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'branches'
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
    
    def __str__(self):
        return f"{self.business.name} - {self.name}"

class BusinessField(models.Model):
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'business_fields'
        verbose_name = 'Business Field'
        verbose_name_plural = 'Business Fields'

class Permission(models.Model):
    menu_name = models.CharField(max_length=50)
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.menu_name

class Membership(models.Model):
    user = models.ForeignKey("account.User", on_delete=models.CASCADE, related_name="authusermodel")
    business = models.ForeignKey("business.Business", on_delete=models.CASCADE)
    tag = models.CharField(max_length=255, blank=True, null=True)

    role = models.CharField(max_length=255, default="CLIENT")
    permissions = models.ManyToManyField(Permission, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table ='memberships'
        verbose_name = 'Membership'
        verbose_name_plural = 'Memberships'

    def __str__(self):
        return f"{self.user.full_name} - {self.business.name} ({self.role})"
    
class Role(models.Model):
    """Customizable roles that can be created by users"""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False, help_text="Is this a default role for the business?")
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'name')
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.business.name})"

class Subscription(models.Model):
    class SubscriptionTier(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        PRO = 'PRO', 'Pro'
        ENTERPRISE = 'ENTERPRISE', 'Enterprise'
    
    class PlatformType(models.TextChoices):
        WEB = 'web', 'Web'
        MOBILE = 'mobile', 'Mobile'
        TELEGRAM_BOT_WEB = 'telegram_bot_web', 'Telegram Bot and Web'
    
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE)
    subscription_type = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.BASIC  
    )
    platform_type = models.CharField(
        max_length=20,
        choices=PlatformType.choices,
        default=PlatformType.TELEGRAM_BOT_WEB
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_auto_renew = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_active(self):
        """Check if subscription is currently active"""
        now = timezone.now().date()
        return (
            self.start_date <= now and 
            (self.end_date is None or self.end_date >= now)
        )
    
    def is_future(self):
        """Check if subscription starts in the future"""
        return self.start_date > timezone.now().date()
    
    def days_remaining(self):
        """Calculate remaining days for active subscriptions"""
        if not self.is_active():
            return 0
        if self.end_date is None:  # Lifetime subscription
            return float('inf')
        return (self.end_date - timezone.now().date()).days
    
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-start_date']
    
    def __str__(self):
        return f'{self.business.name} - {self.get_subscription_type_display()} ({self.platform_type})'

class TrafficStat(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='traffic_stats')
    platform = models.CharField(max_length=20)  # TELEGRAM yoki WEB
    date = models.DateField()
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('business', 'platform', 'date')