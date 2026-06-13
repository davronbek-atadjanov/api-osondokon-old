from django.db import models

class Telegram_bot(models.Model):
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE)
    business_link = models.CharField(max_length=255)
    token = models.CharField(max_length=255)

    class Meta:
        db_table = 'telegram_bots'
        
    def __str__(self):
        return self.business.name