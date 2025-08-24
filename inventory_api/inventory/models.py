from django.db import models
from django.db.models import Q


# Create your models here.
class Category(models.Model):
    """
    Represents a category for grouping and organizing products.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Represents an individual item in the inventory.
    """
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT, 
        related_name="products"
    )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)  
    quantity_in_stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Enforces data integrity at the database level
        constraints = [
            models.CheckConstraint(
                check=Q(quantity_in_stock__gte=0),
                name="product_quantity_nonnegative"
            ),
            models.UniqueConstraint(
                fields=["name", "category"],
                name="unique_product_in_category"
            ),
        ]
        # Optimizes database performance for common queries
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
            models.Index(fields=["quantity_in_stock"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"