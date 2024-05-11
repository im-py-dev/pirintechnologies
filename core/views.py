from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone

from .models import Invoice, Product, Payment

from xhtml2pdf import pisa

@login_required
def home(request):
    user_invoices = Invoice.objects.filter(user=request.user)
    return render(request, 'home.html', {'invoices': user_invoices, 'username': request.user.username})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            
            product = Product.objects.get(pk=1)
            invoice = Invoice.objects.create(user=user, product=product)

            login(request, user)

            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def download_pdf(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    html = render_to_string('invoice_template.html', {'invoice': invoice})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


@login_required
def make_payment(request, invoice_id, payment_link_id):
    invoice = Invoice.objects.get(id=invoice_id)
    payment = Payment.objects.get(id=payment_link_id)

    if invoice.paid:
        return render(request, 'payment_success.html', {'invoice': invoice, 'payment': payment })

    if payment.expiration_date > timezone.now():
        payment.mark_as_successful()
        invoice.mark_as_paid()
        
        return render(request, 'payment_success.html', {'invoice': invoice, 'payment': payment })
    
    else:
        return render(request, 'payment_expired.html')
    

@login_required
def create_invoice(request):
    user = request.user
    product = Product.objects.get(pk=1)
    new_invoice = Invoice.objects.create(user=user, product=product)
    return redirect('/')


@login_required
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if invoice.paid:
        successful_payment = Payment.objects.filter(invoice=invoice, successful=True).first()
        return render(request, 'view_invoice.html', {'invoice': invoice, 'payment_link': successful_payment})

    last_payment = Payment.objects.filter(invoice=invoice).order_by('-created_at').first()

    if not last_payment:
        first_payment = Payment.objects.create(invoice=invoice)

    return render(request, 'view_invoice.html', {
        'invoice': invoice,
        'payment_link': last_payment or first_payment,
        })


@login_required
def create_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    new_payment = Payment.objects.create(invoice=invoice)
    return render(request, 'view_invoice.html', {'invoice': invoice, 'payment_link': new_payment})
