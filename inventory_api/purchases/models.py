from django.db import models
from inventory.models import Product, Supplier
from django.db.models import Sum

# Create your models here.
class Purchase(models.Model):
    supplier = models.ForeignKey(
        'inventory.Supplier',
        on_delete=models.PROTECT,
        related_name='purchases',
        help_text="The supplier from whom the purchase was made."
    )
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time of the purchase."
    )
    
    @property
    def total_amount(self):
        return self.items.aggregate(
            total=Sum(models.F('quantity') * models.F('unit_price'))
        )['total'] or 0.00
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f'Purchase {self.id} from {self.supplier.name}'

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="The purchase this item belongs to."
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        help_text="The product purchased."
    )
    quantity = models.PositiveIntegerField(
        help_text="The quantity of the product purchased."
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="The price per unit at the time of purchase."
    )

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"