from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone

from .models import Invoice, Product, Payment
from .utils import generate_random_username, payment_required, create_first_invoice
from xhtml2pdf import pisa
from .forms import CustomSignupForm


@login_required
@payment_required
def home(request):
    user_invoices = Invoice.objects.filter(user=request.user)
    return render(request, 'home.html', {'invoices': user_invoices, 'username': request.user.username})


@login_required
def invoices(request):
    user_invoices = Invoice.objects.filter(user=request.user)
    return render(request, 'Invoices.html', {'invoices': user_invoices, 'username': request.user.username})


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
        generated_username = request.session.get('generated_username')
        print("generated_username", generated_username)

        form = CustomSignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            user.username = generated_username
            user.save()
            create_first_invoice(user)
            login(request, user)
            return redirect('/')

        else:
            # Handle the case where the form is not valid
            print("Form is not valid")
            print("form.errors", form.errors)
            return render(request, 'signup.html', {'form': form, 'generated_username': generated_username})
        
    else:
        form = CustomSignupForm()
        generated_username = generate_random_username()
        request.session['generated_username'] = generated_username

    return render(request, 'signup.html', {'form': form, 'generated_username': generated_username})


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
        return render(request, 'payment_success.html', {'invoice': invoice, 'payment': payment, 'username': request.user.username })

    if payment.expiration_date > timezone.now():
        payment.mark_as_successful()
        invoice.mark_as_paid()
        
        return render(request, 'payment_success.html', {'invoice': invoice, 'payment': payment, 'username': request.user.username })
    
    else:
        return render(request, 'payment_expired.html', {'username': request.user.username})


@login_required
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if invoice.paid:
        successful_payment = Payment.objects.filter(invoice=invoice, successful=True).first()
        return render(request, 'view_invoice.html', {'invoice': invoice, 'payment_link': successful_payment, 'username': request.user.username})

    last_payment = Payment.objects.filter(invoice=invoice).order_by('-created_at').first()

    if not last_payment:
        first_payment = Payment.objects.create(invoice=invoice)

    return render(request, 'view_invoice.html', {
        'invoice': invoice,
        'payment_link': last_payment or first_payment,
        'username': request.user.username,
        })


@login_required
def create_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    new_payment = Payment.objects.create(invoice=invoice)
    return render(request, 'view_invoice.html', {'invoice': invoice, 'payment_link': new_payment, 'username': request.user.username})
