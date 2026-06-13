from django.db import models
from django.db.models import Case, Value, When, IntegerField
from apps.business.models import Subscription


# model Order {
#   id           String      @id @default(uuid())
#   userId       String
#   user         User        @relation(fields: [userId], references: [id])
#   businessId   String
#   business     Business    @relation(fields: [businessId], references: [id])
#   orderItems   OrderItem[]
#   totalAmount  Decimal
#   createdAt    DateTime    @default(now())
#   updatedAt    DateTime    @updatedAt
# }

# model OrderItem {
#   id        String  @id @default(uuid())
#   orderId   String
#   order     Order   @relation(fields: [orderId], references: [id])
#   productId Int
#   product   Product @relation(fields: [productId], references: [id])
#   quantity  Int
#   price     Decimal
# }


class Order(models.Model):
    class OrderSource(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    user = models.ForeignKey('account.User', on_delete=models.CASCADE)

    business = models.ForeignKey('business.Business', on_delete=models.CASCADE)
    branch = models.ForeignKey(
        'business.Branch', on_delete=models.CASCADE, null=True, blank=True)
    operator = models.ForeignKey(
        'business.Membership', on_delete=models.SET_NULL, null=True, blank=True)

    source = models.CharField(
        max_length=20,
        choices=OrderSource.choices,
        default=OrderSource.CUSTOMER
    )

    payment_method = models.CharField(max_length=255, default="CASH")
    comment = models.TextField(blank=True)

    address = models.JSONField(default=dict, blank=True)

    delivery = models.CharField(max_length=255, default="DELIVERY")
    status = models.CharField(max_length=255, default="NEW")
    is_paid = models.BooleanField(default=False)

    platform = models.CharField(max_length=255, default="WEB")
    total_amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

        ordering = [
            Case(
                When(status="NEW", then=Value(1)),
                When(status="PROCESSING", then=Value(2)),
                When(status="DELIVERING", then=Value(3)),
                When(status="COMPLETED", then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            ),
            "-created_at"
        ]

    def __str__(self):
        return str(self.id)

class OrderItem(models.Model):
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE)
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    variant = models.ForeignKey(
        'product.ProductVariant',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    quantity = models.IntegerField()
    price = models.IntegerField(default=0)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return str(self.id)