from django.db import models

# model Category {
#   id         Int       @id @default(autoincrement())
#   name       String
#   logo       String?
#   picture    String?
#   products   Product[]
#   business   Business  @relation(fields: [businessId], references: [id])
#   businessId String
# }



class Category(models.Model):
    # Multi-language support
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255, blank=True, null=True)
    name_tr = models.CharField(max_length=255, blank=True, null=True)

    logo = models.CharField(max_length=4096, blank=True, null=True)
    picture = models.CharField(max_length=4096, blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='children'
    )
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

        indexes = [
            models.Index(fields=['business', 'name_uz']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name_uz or self.name_ru or self.name_tr or "Unnamed Category"