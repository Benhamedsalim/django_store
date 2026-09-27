from django.conf import settings
from django.db import models
from django.contrib.sessions.models import Session
from checkout.models import Transaction

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    featured = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    short_description = models.TextField(null=True)
    description = models.TextField()
    image = models.ImageField()
    pdf_file = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    @property
    def pdf_file_url(self):
        if self.pdf_file:
            return settings.SITE_URL + self.pdf_file.url
        return ''

class Order(models.Model):
    tranaction = models.OneToOneField(Transaction, on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.id)
    @property
    def customer_name(self):
        return f"{self.customer.get('first_name', '')} {self.customer.get('last_name', '')}"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class Slider(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(max_length=500)
    image = models.ImageField(null=True)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    items = models.JSONField(default=dict)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
