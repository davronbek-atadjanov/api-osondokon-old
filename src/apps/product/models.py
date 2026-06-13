from django.db import models

class Product(models.Model):
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE)

    # name fields
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, blank=True, null=True)
    name_tr = models.CharField(max_length=255, blank=True, null=True)

    # short description
    short_description_uz = models.TextField(blank=True)
    short_description_ru = models.TextField(blank=True)
    short_description_tr = models.TextField(blank=True)
    
    # full description  
    description_uz = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_tr = models.TextField(blank=True)
    
    images = models.JSONField(default=list)  # list of image URLs
    attributes = models.JSONField(default=dict, null=True, blank=True)  # { "color": ["red", "blue"], "storage": ["64GB"] }
    attributes_images = models.JSONField(default=dict, null=True, blank=True)  
    
    features = models.JSONField(default=dict, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    # keraksiz field
    price = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    order_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return self.name_uz or self.name_ru or self.name_tr or "Unnamed Product"
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)    
    combination = models.JSONField(default=dict, null=True, blank=True) # {"color": "red", "storage": "8/128"}
   
    price = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    sale_price = models.PositiveIntegerField(default=0)

    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_variants'
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'

    def __str__(self):
        return f"{self.product.name_uz}".strip()