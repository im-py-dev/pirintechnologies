from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
        
    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    
    path('invoice/<int:invoice_id>/create_payment/', views.create_payment, name='create_payment'),
    path('invoice/<int:invoice_id>/pay/<int:payment_link_id>/', views.make_payment, name='make_payment'),

    path('invoice/<int:invoice_id>/download_pdf/', views.download_pdf, name='download_pdf'),
]
