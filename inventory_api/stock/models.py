from django.db import models
from inventory.models import Product
from purchases.models import Purchase
from sales.models import Sale

# Create your models here.
MOVEMENT_CHOICES = (
    ('IN', 'In'),
    ('OUT', 'Out'),
)

class StockMovement(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        help_text="The product whose stock was moved."
    )
    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_CHOICES,
        help_text="Type of movement: 'IN' for purchases, 'OUT' for sales."
    )
    quantity = models.PositiveIntegerField(
        help_text="The quantity of the product moved."
    )
    related_purchase = models.ForeignKey(
        Purchase,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Reference to the purchase transaction, if applicable."
    )
    related_sale = models.ForeignKey(
        Sale,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Reference to the sale transaction, if applicable."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time of the stock movement."
    )

    class Meta:
        verbose_name_plural = "Stock Movements"
        ordering = ['-timestamp']  
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.movement_type} - {self.product.name} - {self.quantity}"