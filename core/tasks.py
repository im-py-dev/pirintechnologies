from celery import shared_task
from core.models import Invoice, Product
from django.contrib.auth.models import User


@shared_task
def generate_new_invoice(user_id, product_id, start_date, end_date):
    user = User.objects.get(id=user_id)
    product = Product.objects.get(id=product_id)
    new_invoice = Invoice.objects.create(user=user, product=product, start_date=start_date, end_date=end_date)
    return new_invoice
