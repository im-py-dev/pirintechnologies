import random
from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = 'Create a product with random data'

    def handle(self, *args, **options):
        # Generate random data for the product
        name = f"Product-1"
        description = f"This is a product with ID: 1"
        price = 99.99

        # Create the product
        product = Product.objects.create(name=name, description=description, price=price)
        self.stdout.write(self.style.SUCCESS(f"Successfully created product: {product}"))
