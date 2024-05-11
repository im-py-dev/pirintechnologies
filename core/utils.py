from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.utils import timezone
from .models import Invoice, Product, Payment


def payment_required(function=None, redirect_field_name='next', login_url=None):
    """
    Decorator for views that checks that the user's invoice is paid and its end_date not finished yet,
    redirecting to the payment page if necessary.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _redirect_to_login(request.get_full_path(), login_url, redirect_field_name)

            latest_invoice = request.user.invoice_set.order_by('-created_at').first()

            # not needed but only if we want delete the invoice (user will has no invoices) so this will fix it
            if not latest_invoice:
                product = Product.objects.get(pk=1)
                invoice = Invoice.objects.create(user=request.user, product=product)
                return redirect(reverse('view_invoice', args=[invoice.id]))

            if not latest_invoice.paid:
                return redirect(reverse('view_invoice', args=[latest_invoice.id]))

            if latest_invoice.end_date < timezone.now():
                product = Product.objects.get(pk=1)
                new_invoice = Invoice.objects.create(user=request.user, product=product)
                return redirect(reverse('view_invoice', args=[new_invoice.id]))

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
