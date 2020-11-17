from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class Customer(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=30, blank=True)

class Address(models.Model):
    addressId = models.AutoField(auto_created=True, primary_key=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, default=' ', null=True, blank=True,related_name='address')
    address1 = models.CharField(
        "Address line 1",
        max_length=1024,
    )

    address2 = models.CharField(
        "Address line 2",
        max_length=1024,
        blank=True
    )

    zip_code = models.CharField(
        "ZIP / Postal code",
        max_length=12,
    )

    city = models.CharField(
        "City",
        max_length=1024,
    )

    state= models.CharField(
        "State",
        max_length=1024
    )

    country = models.CharField(
        "Country",
        max_length=1024,
    )

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return "%s" % self.addressId


class Category(models.Model):
    categoryId = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=1024)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return "%s" % self.name

class Item(models.Model):
    itemId = models.AutoField(auto_created=True, primary_key=True)
    itemName = models.CharField(
        "Name",
        max_length=1024,
    )
    category = models.ForeignKey(Category,
                                  on_delete=models.CASCADE,
                                  related_name='category'
                                  )
    itemImage = models.ImageField(upload_to='images',null=True,blank=True)
    itemOwner = models.ForeignKey(Customer,
                                  on_delete=models.CASCADE,
                                  related_name='my_items'
                                  )
    itemAvaialable = models.BooleanField()
    costPerItem = models.IntegerField()
    itemDescription = models.TextField(null=True,blank=True)
    itemAddedDate = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.itemName

    def get_absolute_url(self):
        return reverse('RentalApp:item_details',
                       args=[self.itemId])
    def getcontact(self):
        return self.itemOwner.phone_number

class RentItems(models.Model):
    rentId = models.AutoField(auto_created=True, primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rentStartDate = models.DateField()
    rentEndDate = models.DateField(null=True)
    renterName = models.CharField(max_length=1024)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    renterPhoneNumber = models.CharField(validators=[phone_regex], max_length=30, blank=True)
    totalCost = models.FloatField(null=True)
    notes = models.TextField(null=True,blank=True)

    def __str__(self):
        return "%s" % self.rentId

# brew install graphviz
# pip install pyparsing pydot
# (venv) daweili@Daweis-MacBook-Pro MAH % python manage.py graph_models -a > erd.dot
# (venv) daweili@Daweis-MacBook-Pro MAH % python manage.py graph_models -a -g -o  ERD.png

from django.db import models

# Create your models here.
