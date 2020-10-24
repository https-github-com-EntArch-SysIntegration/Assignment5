from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class Customer(AbstractUser):
    phone_number = models.CharField(max_length=30, blank=True)

class Address(models.Model):
    addressId = models.AutoField(auto_created=True, primary_key=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, default=' ', null=True, blank=True)
    address1 = models.CharField(
        "Address line 1",
        max_length=1024,
    )

    address2 = models.CharField(
        "Address line 2",
        max_length=1024,
    )

    zip_code = models.CharField(
        "ZIP / Postal code",
        max_length=12,
    )

    city = models.CharField(
        "City",
        max_length=1024,
    )

    country = models.CharField(
        "Country",
        max_length=3,
    )

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"


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
    itemImage = models.ImageField(upload_to='images')
    itemOwner = models.ForeignKey(Customer,
                                  on_delete=models.CASCADE,
                                  related_name='my_items'
                                  )
    itemAvaialable = models.BooleanField()
    costPerItem = models.IntegerField()
    itemDescription = models.TextField()
    itemAddedDate = models.DateField()

    def __str__(self):
        return "%s" % self.itemId

class RentItems(models.Model):
    rentId = models.AutoField(auto_created=True, primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rentStartDate = models.DateTimeField()
    rentEndDate = models.DateTimeField()
    renterName = models.CharField(max_length=1024)
    renterPhoneNumber = models.CharField(max_length=30, blank=True)
    totalCost = models.FloatField()

    def __str__(self):
        return "%s" % self.rentId

# brew install graphviz
# pip install pyparsing pydot
# (venv) daweili@Daweis-MacBook-Pro MAH % python manage.py graph_models -a > erd.dot
# (venv) daweili@Daweis-MacBook-Pro MAH % python manage.py graph_models -a -g -o  ERD.png

from django.db import models

# Create your models here.
