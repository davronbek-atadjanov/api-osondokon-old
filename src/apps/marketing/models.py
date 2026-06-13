from django.db import models

class EmailTemplate(models.Model):
    CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )

    name = models.CharField(max_length=100)

    content = models.TextField()
    subject = models.CharField(max_length=100)

    status = models.CharField(max_length=32, choices=CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'

    def __str__(self):
        return self.name

class SmsTemplate(models.Model):
    CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )

    name = models.CharField(max_length=100)
    content = models.TextField()

    status = models.CharField(max_length=32, choices=CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'SMS Template'
        verbose_name_plural = 'SMS Templates'

    def __str__(self):
        return self.name
    
class Banner(models.Model):
    image = models.CharField(max_length=4096, blank=True, null=True)
    desktop_image = models.CharField(max_length=4096, blank=True, null=True)
    link = models.CharField(max_length=4096, blank=True, null=True)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='banners')

    class Meta:
        db_table = 'banners'
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'

    def __str__(self):
        return self.link