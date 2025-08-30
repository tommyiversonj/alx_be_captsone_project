from django.db import models
from django.db.models import Sum
from inventory.models import Product

# Create your models here.
class Sale(models.Model):
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time of the sale."
    )
    customer_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Name of the customer (optional)."
    )
    
    @property
    def total_amount(self):
        return self.items.aggregate(
            total=Sum(models.F('quantity') * models.F('unit_price'))
        )['total'] or 0.00
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f'Sale {self.id}'

class SaleItem(models.Model):
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="The sale this item belongs to."
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        help_text="The product sold."
    )
    quantity = models.PositiveIntegerField(
        help_text="The quantity of the product sold."
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="The price per unit at the time of the sale."
    )

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"