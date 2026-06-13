import string
import random
import uuid
import json
import base64
import threading
import re
from apps.business.models import Business
from apps.telegrambot.models import Telegram_bot
from graphql import GraphQLError
import logging
from apps.business.service import (
    check_telegram_token, remove_telegram_bot, create_telegram_bot_async, remove_vercel_domain, add_vercel_domain
)

logger = logging.getLogger(__name__)

def sanitize_domain_part(domain_part):
    """Sanitize a domain part (subdomain or custom domain) to only allow valid characters"""
    if not domain_part:
        return ""

    # Convert to lowercase
    domain_part = domain_part.lower()

    # Remove all invalid characters (keep only letters, numbers, hyphens and underscores)
    # Also replace multiple dots with single dot
    domain_part = re.sub(r'[^a-z0-9\-_]', '', domain_part)

    # Remove leading/trailing hyphens/underscores
    domain_part = domain_part.strip('-_')

    # Ensure it's not empty after sanitization
    if not domain_part:
        raise ValueError(
            "Domain contains no valid characters after sanitization")

    return domain_part

def generate_telegram_subdomain(prefix="tgbot", length=10):
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}-{random_part}.osonstore.uz"

def generate_business_hash_id(platforms_str=None):
    """Generate a unique hash ID for a business based on its domain configuration"""
    try:
        if not platforms_str:
            raise ValueError("No platforms config")

        platforms = json.loads(platforms_str)
        web_config = platforms.get("web", {})

        if not web_config.get("enabled"):
            raise ValueError("Web config disabled")

        domain_type = web_config.get("domainType")
        domain = None

        if domain_type == "custom":
            domain = web_config.get("customDomain")
            if domain:
                parts = domain.split(".")
                if len(parts) > 1:
                    sanitized = [sanitize_domain_part(p) for p in parts[:-1]]
                    sanitized.append(parts[-1])  # TLD ni saqlaymiz
                    domain = ".".join(sanitized)
                else:
                    domain = sanitize_domain_part(domain)

        elif domain_type == "subdomain":
            subdomain = web_config.get("subdomain")
            if subdomain:
                domain = f"{sanitize_domain_part(subdomain)}.osonstore.uz"

        if domain:
            return base64.b64encode(domain.encode()).decode()

        # Agar yuqorida domain aniqlanmasa → random id
        raise ValueError("No valid domain found")

    except Exception as e:
        logger.warning(f"Error generating business hash ID: {e}")
        uid = uuid.uuid4()
        return base64.urlsafe_b64encode(uid.bytes).rstrip(b"=").decode()

def process_business_fields(business, kwargs):
    """Process and set business fields from kwargs"""
    json_fields = ['payment_methods', 'platforms',
                   'languages', 'working_days', 'social_info']

    for key, value in kwargs.items():
        if key in json_fields and value:
            try:
                value = json.loads(value)
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Failed to parse JSON for field {key}: {str(e)}")
                # Keep original string value if JSON parsing fails

        setattr(business, key, value)

    return business

def get_domain_from_platforms(platforms_data):
    """Extract domain information from platforms data"""
    web_config = platforms_data.get('web', {})

    if web_config.get('enabled', False):
        domain_type = web_config.get("domainType")

        if domain_type == "custom":
            return web_config.get("customDomain")
        elif domain_type == "subdomain":
            subdomain = web_config.get('subdomain')
            if subdomain:
                sanitized_subdomain = sanitize_domain_part(subdomain)
                return f"{sanitized_subdomain}.osonstore.uz"

    return None

def is_platform_available(platforms_data, exclude_business_id=None):
    """Check if platform configurations (domain and telegram bot) are available"""
    if not platforms_data:
        return True
        
    web_config = platforms_data.get('web', {})
    telegram_config = platforms_data.get('telegram', {})
    
    # Domain tekshirish
    if web_config.get('enabled'):
        domain = get_domain_from_platforms(platforms_data)
        if domain:
            businesses = Business.objects.all()
            if exclude_business_id:
                businesses = businesses.exclude(id=exclude_business_id)
                
            for business in businesses:
                try:
                    if business.platforms:
                        if isinstance(business.platforms, str):
                            existing_platforms = json.loads(business.platforms)
                        else:
                            existing_platforms = business.platforms  # already dict
                        existing_domain = get_domain_from_platforms(existing_platforms)
                        if existing_domain and existing_domain.lower() == domain.lower():
                            raise GraphQLError(f"Domain '{domain}' is already in use")
                except Exception as e:
                    logger.error(f"Error checking domain: {str(e)}")
                    continue
    
    # Telegram bot token tekshirish
    if telegram_config.get('enabled'):
        bot_token = telegram_config.get('botToken')
        if bot_token:
            # Existing bot tokens tekshirish
            existing_bot = Telegram_bot.objects.filter(token=bot_token)
            if exclude_business_id:
                existing_bot = existing_bot.exclude(business_id=exclude_business_id)
                
            if existing_bot.exists():
                raise GraphQLError("This Telegram bot token is already in use")
            
            # Telegram API orqali token validatsiya
            is_valid, result = check_telegram_token(bot_token)
            if not is_valid:
                raise GraphQLError(f"Invalid Telegram bot token: {result}")
    
    return True

def process_telegram_config(business, platforms_str):
    try:
        telegram_config = platforms_str.get('telegram', {})

        # Agar telegram disabled bo'lsa yoki bot token yo'q bo'lsa, mavjud botni o'chiramiz
        if not telegram_config.get('enabled', False):
            remove_telegram_bot(business)
            return None

        bot_token = telegram_config.get('botToken')

        # Calculate business link
        business_link = generate_telegram_subdomain()       

        # Existing bot check
        existing_bot = Telegram_bot.objects.filter(business=business).first()
        
        if not existing_bot:
            threading.Thread(
                target=create_telegram_bot_async,
                args=(business, bot_token, business_link),
                daemon=True
            ).start()

        elif existing_bot.token != bot_token:
            remove_telegram_bot(business)
            threading.Thread(
                target=create_telegram_bot_async,
                args=(business, bot_token, business_link),
                daemon=True
            ).start()

        else:
            return None
        
    except Exception as e:
        logger.error(f"Error processing Telegram config: {str(e)}")
    return base64.b64encode(business_link.encode()).decode()


def process_platforms_config(business, platforms_str, previous_platforms_str=None):
    """Process platforms configuration including domain setup"""
    if not platforms_str:
        return

    try:
        new_platforms = platforms_str
        if isinstance(platforms_str, str):
            new_platforms = json.loads(platforms_str)
        else:
            new_platforms = platforms_str
        
        if not isinstance(previous_platforms_str, dict):
            old_platforms = json.loads(previous_platforms_str) if previous_platforms_str else {}
        else:
            old_platforms = previous_platforms_str

        # Handle web configuration (domains)
        new_domain = get_domain_from_platforms(new_platforms)
        old_domain = get_domain_from_platforms(old_platforms)

        # If domain has changed, update Vercel and CORS
        if new_domain != old_domain:
            # Remove old domain if it exists
            if old_domain:
                remove_vercel_domain(old_domain)
                remove_vercel_domain(f"www.{old_domain}")

            # Add new domain if it exists
            if new_domain:
                add_vercel_domain(new_domain)
                add_vercel_domain(f"www.{new_domain}")

            hash_id = generate_business_hash_id(platforms_str)
            business.hash_id = hash_id

        # Process Telegram configuration
        tg_hash_id = process_telegram_config(business, new_platforms)
        if tg_hash_id:
            business.tg_hash_id = tg_hash_id
    except Exception as e:
        logger.error(f"Error processing platforms config: {str(e)}")
    return business
