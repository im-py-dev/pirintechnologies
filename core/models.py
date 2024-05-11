from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        self.amount = self.product.price
        super().save(*args, **kwargs)

    def mark_as_paid(self):
        if not self.paid:
            self.paid = True
            self.start_date = timezone.now()
            self.end_date = self.start_date + timezone.timedelta(days=30)

            self.save()

    def __str__(self):
        return f"Invoice for {self.user.username}"
    

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_link = models.CharField(max_length=100, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True)
    successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for {self.invoice}"

    def save(self, *args, **kwargs):
        if not self.expiration_date:
            self.expiration_date = timezone.now() + timezone.timedelta(hours=2)
        super().save(*args, **kwargs)

    def mark_as_successful(self):
        if not self.successful:
            self.successful = True
            self.save()

    @property
    def expired(self):
        # Check if the payment link is expired
        return timezone.now() >= self.expiration_date or self.successful
