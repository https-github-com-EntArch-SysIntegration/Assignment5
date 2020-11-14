import self as self
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Submit, Button
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.handlers import exception
from django.forms import forms
from django.http import request
from django.shortcuts import render, redirect, get_list_or_404

# Create your views here.
from .forms import CustomUserCreationForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from .models import Category, Item, Address
from .forms import CustomUserSignupForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

def item_list(request):
    categories = Category.objects.all()
    items = Item.objects.filter(itemAvaialable=True)
    request.session["addressId"] = None
    if not request.user.is_anonymous:
        try:
            addresses = Address.objects.filter(customer=request.user)
            for add in addresses:
                address = get_object_or_404(Address, addressId=add.addressId)
                request.session["addressId"] = address.addressId
        except Address.DoesNotExist:
            address = None

    return render(request,
                  'home.html',
                  {'categories': categories,
                   'items': items})

def item_details(request, id):
    item = get_object_or_404(Item,
                                itemId=id)

    return render(request,
                  'itemdetails.html',
                  {'item': item})

@login_required(login_url = '/users/login/')
def product_details(request,id):
    item = get_object_or_404(Item,
                                itemId=id)
    return render(request,
                  'productDetails.html',
                  {'item': item})

class AddressView(LoginRequiredMixin,DetailView):
    model = Address
    template_name = 'address.html'
    login_url = '/users/login/'

class UpdateAddressView(LoginRequiredMixin,UpdateView):
    model = Address
    template_name = 'editAddress.html'
    fields = ('address1','address2', 'zip_code','city','country')
    login_url = '/users/login/'

    def form_valid(self, form):
        form.is_valid()
        form.instance.customer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('RentalApp:address',args=[self.request.user.address.pk])

class AddAddressView(LoginRequiredMixin,CreateView):
    model = Address
    template_name = 'addAddress.html'
    fields = ('address1','address2', 'zip_code','city','country')
    login_url = '/users/login/'

    def form_valid(self, form):
        form.is_valid()
        form.instance.customer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('RentalApp:item_list')

class SignUpView(CreateView):
    form_class = CustomUserSignupForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required(login_url = '/users/login/')
def PasswordChangeView(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('changePassword')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/changePassword.html', {
        'form': form
    })

@login_required(login_url = '/users/login/')
def myProducts(request):
    address = None
    try:
        addresses = Address.objects.filter(customer=request.user)
        for add in addresses:
            address = get_object_or_404(Address, addressId=add.addressId)
    except Address.DoesNotExist:
        address = None

    if not request.user.is_anonymous:
        items = Item.objects.filter(itemOwner=request.user)
    else:
        items = None

    return render(request,
                  'myProducts.html',
                  {'items': items,
                   'address': address})

class AddProductView(LoginRequiredMixin,CreateView):
    model = Item
    template_name = 'addProduct.html'
    image = forms.FileField(required=False)
    fields = ('itemName',
                    'category',
                    'itemImage',
                    'itemAvaialable',
                    'costPerItem',
                    'itemDescription')
    login_url = '/users/login/'

    def form_valid(self, form):
        form.is_valid()
        form.instance.itemOwner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('RentalApp:my_products')



class EditProductView(LoginRequiredMixin,UpdateView):
    model = Item
    template_name = 'editProduct.html'
    login_url = '/users/login/'
    fields = ('itemName',
                    'category',
                    'itemImage',
                    'itemAvaialable',
                    'costPerItem',
                    'itemDescription')

    def form_valid(self, form):
        form.is_valid()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('RentalApp:my_products')

class DeleteProductView(LoginRequiredMixin,DeleteView):
    model = Item
    template_name = 'deleteProduct.html'
    success_url = reverse_lazy('RentalApp:my_products')
    login_url = '/users/login/'