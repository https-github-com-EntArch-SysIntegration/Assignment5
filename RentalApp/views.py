import csv
import datetime

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.forms import forms
from django.http import HttpResponse
from django.shortcuts import redirect

# Create your views here.
from reportlab.lib.styles import getSampleStyleSheet

from .forms import CustomUserCreationForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

from .models import Category, Item, Address, RentItems
from .forms import CustomUserSignupForm,RentProductForm, EndRentProductForm
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table

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

    def form_valid(self, form):
        form.is_valid()
        form.instance.customer = self.request.user
        return super().form_valid(form)

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

class StartRentView(LoginRequiredMixin,CreateView):
    form_class = RentProductForm
    template_name = 'rental.html'
    success_url = reverse_lazy('RentalApp:rental_history')
    login_url = '/users/login/'

    def form_valid(self, form):
        form.is_valid()
        item = get_object_or_404(Item, itemId=form.instance.item.itemId)
        item.itemAvaialable = False
        item.save()
       # form.instance.item = item
        return super().form_valid(form)

class RentalHisoryView(LoginRequiredMixin,ListView):
    model = RentItems
    template_name = 'rentalHist.html'
    login_url = '/users/login/'

class updateRentItemView(LoginRequiredMixin,UpdateView):
    model = RentItems
    form_class = EndRentProductForm
    template_name = 'rentEnd.html'
    login_url = '/users/login/'

    def form_valid(self, form):
        form.is_valid()
        item = get_object_or_404(Item, itemId=form.instance.item.itemId)
        rent = item.costPerItem
        item.itemAvaialable = True
        item.save()
        days = (form.instance.rentEndDate - form.instance.rentStartDate).days
        form.instance.totalCost = days * rent
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('RentalApp:rent_overView', kwargs={'pk': self.object.pk})

class rentDetailView(LoginRequiredMixin,DetailView):
    model = RentItems
    template_name = 'rentOverView.html'
    login_url = '/users/login/'

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rental_history.csv"'
    writer = csv.writer(response)
    writer.writerow(['ItemName','RentstartDate','RentEndDate','Totalcost','RenterName','RenterPhoneNumber','Notes'])
    item_list = Item.objects.filter(itemOwner=request.user)
    rentItems = RentItems.objects.filter(item__in=item_list)
    for item in rentItems:
        writer.writerow([item.item.itemName,item.rentStartDate,item.rentEndDate,item.totalCost,item.renterName,item.renterPhoneNumber,item.notes])
    return response


def export_pdf(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()
    data=[]
    my_doc = SimpleDocTemplate(buffer)
    sample_style_sheet = getSampleStyleSheet()
    data += [['Rental History']]
    item_list = Item.objects.filter(itemOwner = request.user)
    rentItems = RentItems.objects.filter(item__in=item_list)
    data += [['ItemName', 'RentStartDate', 'RentEndDate','RenterName', 'Renter Phonenumber', 'Notes', 'TotalRent']]
    for i in rentItems:
        itemName = str(i.item.itemName).encode('utf-8')
        rentStartDate = str(i.rentStartDate).encode('utf-8')
        renterName = str(i.renterName).encode('utf-8')
        renterPhoneNumber = str(i.renterPhoneNumber).encode('utf-8')
        notes = str(i.notes).encode('utf-8')
        rentEndDate = str(i.rentEndDate).encode('utf-8')
        totalCost = str(i.totalCost).encode('utf-8')

        # Add this loop's step row into data array
        data += [[itemName, rentStartDate, rentEndDate, renterName, renterPhoneNumber, notes, totalCost]]

    table_data = Table(data, colWidths=None, rowHeights=None)
    my_doc.build([table_data])
    # Create the PDF object, using the buffer as its "file."
    pdf_value = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rental_history.pdf"'

    response.write(pdf_value)
    return response