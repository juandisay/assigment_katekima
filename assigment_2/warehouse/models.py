from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Item(BaseModel):
    code = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    stock = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        if self.stock < 0:
            raise ValidationError("Stock cannot be negative.")
        if self.balance < 0:
            raise ValidationError("Balance cannot be negative.")

    class Meta:
        ordering = ['code']


class PurchaseHeader(BaseModel):
    code = models.CharField(max_length=50, primary_key=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Purchase {self.code} - {self.date}"

    class Meta:
        ordering = ['-date', 'code']


class PurchaseDetail(BaseModel):
    header = models.ForeignKey(PurchaseHeader, on_delete=models.PROTECT, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='purchase_details')
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_quantity = models.DecimalField(max_digits=15, decimal_places=2)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.unit_price <= 0:
            raise ValidationError("Unit price must be positive.")

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            self.remaining_quantity = self.quantity
            self.item.stock += self.quantity
            self.item.balance += (self.quantity * self.unit_price)
            self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase Detail {self.header.code} - {self.item.code}"


class SellHeader(BaseModel):
    code = models.CharField(max_length=50, primary_key=True)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Sale {self.code} - {self.date}"

    class Meta:
        ordering = ['-date', 'code']


class SellDetail(BaseModel):
    header = models.ForeignKey(SellHeader, on_delete=models.PROTECT, related_name='details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='sell_details')
    quantity = models.DecimalField(max_digits=15, decimal_places=2)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.quantity > self.item.stock:
            raise ValidationError("Insufficient stock available.")

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            remaining_to_sell = self.quantity
            total_cost = Decimal('0.0')

            # Get available purchase details with remaining quantity, ordered by date (FIFO)
            purchase_details = PurchaseDetail.objects.filter(
                item=self.item,
                remaining_quantity__gt=0,
                is_deleted=False
            ).order_by('header__date')

            for purchase in purchase_details:
                if remaining_to_sell <= 0:
                    break

                quantity_from_purchase = min(remaining_to_sell, purchase.remaining_quantity)
                cost = (quantity_from_purchase * purchase.unit_price)
                total_cost += cost

                purchase.remaining_quantity -= quantity_from_purchase
                purchase.save()

                remaining_to_sell -= quantity_from_purchase

            if remaining_to_sell > 0:
                raise ValidationError("Insufficient stock available.")

            self.item.stock -= self.quantity
            self.item.balance -= total_cost
            self.item.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale Detail {self.header.code} - {self.item.code}"
