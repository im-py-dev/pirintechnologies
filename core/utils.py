import random

from functools import wraps
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from django.utils import timezone
from .models import CustomUser

from .models import Invoice, Product, Payment


with open('english.txt', 'r') as f:
    words = [word.strip() for word in f.readlines()]


def payment_required(function=None, redirect_field_name='next', login_url=None):
    """
    Decorator for views that checks that the user's invoice is paid and its end_date not finished yet,
    redirecting to the payment page if not.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _redirect_to_login(request.get_full_path(), login_url, redirect_field_name)

            latest_invoice = request.user.invoice_set.order_by('-created_at').first()

            # not needed but only if we want delete the invoice (user will has no invoices) so this will fix it
            if not latest_invoice:
                invoice = create_first_invoice(request.user)
                return redirect(reverse('view_invoice', args=[invoice.id]))

            if not latest_invoice.paid:
                return redirect(reverse('view_invoice', args=[latest_invoice.id]))

            if latest_invoice.end_date < timezone.now():
                product = Product.objects.get(pk=1)
                new_invoice = Invoice.objects.create(user=request.user, product=product)
                return redirect(reverse('view_invoice', args=[new_invoice.id]))
            
            if not latest_invoice.admin_approval:
                return render(request, 'payment_success.html', {'invoice': latest_invoice})

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def _redirect_to_login(next, login_url=None, redirect_field_name='next'):
    """
    Redirects the user to the login page, passing the given 'next' parameter
    """
    if not login_url:
        raise ValueError("The login_url argument must be set or the login() view must be configured in urls.py.")
    login_url_parts = list(login_url)
    if redirect_field_name:
        login_url_parts[4] = urlencode({redirect_field_name: next})
    return redirect(''.join(login_url_parts))


def generate_random_username():
    random_words = random.sample(words, 5)
    new_username = '-'.join(random_words)
    # Check if the username already exists
    while CustomUser.objects.filter(username=new_username).exists():
        return generate_random_username()
    return new_username


def create_first_invoice(user):
    product = Product.objects.get(pk=1)
    return Invoice.objects.create(user=user, product=product)
