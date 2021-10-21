from django.db import models
from model_utils import Choices


class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    desc = models.CharField(max_length=200, null=True, blank=False)

    def __str__(self):
        return self.name


class QuantityType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.FloatField()

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.FloatField()
    rate = models.FloatField()

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    desc = models.CharField(max_length=200, null=True, blank=False, default=None)

    def __str__(self):
        return self.name


class Seller(models.Model):
    name = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=200, null=True, unique=True, blank=False)
    address = models.CharField(max_length=200, null=True, blank=False)

    def __str__(self):
        return self.name


class Worker(models.Model):
    name = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=200, null=True, unique=True, blank=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS = Choices('KG', 'Liter')
    name = models.CharField(max_length=100, unique=True)
    stock_price = models.FloatField()
    price = models.FloatField()
    special = models.FloatField()
    expire = models.DateField(null=True, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    material = models.ManyToManyField(Material)
    quantity_type = models.ForeignKey(QuantityType, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField()
    weight = models.CharField(max_length=100, choices=STATUS, default=STATUS.KG)
    weight_value = models.CharField(max_length=100, default="0")
    extra_quantity = models.FloatField(null=True, default=0)
    barcode = models.CharField(null=True, max_length=100, blank=False, default=" ")
    identifier = models.CharField(null=True, max_length=100, blank=False)
    location = models.CharField(null=True, max_length=100, blank=False)
    alert_if_lower_than = models.IntegerField(null=True)
    image = models.CharField(max_length=100, blank=False, null=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    total = models.FloatField()
    discount = models.FloatField()
    payed = models.FloatField()
    expected_earn = models.FloatField(blank=True, null=True)
    earn = models.FloatField(blank=True, null=True)
    dept = models.FloatField()
    date_published = models.DateTimeField(auto_now_add=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True)
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True)
    paydate = models.DateField()


class InvoiceProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, )
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, )
    quantity = models.FloatField()
    extra_quantity = models.FloatField()
    quantity_type = models.ForeignKey(QuantityType, on_delete=models.CASCADE, )
    piece_price = models.FloatField()
    total = models.FloatField()


class InvoicePayment(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, )
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, )
    add_date = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()


class DailyBoxOperation(models.Model):
    class Month(models.TextChoices):
        ADD = '1', "Add"
        TAKE = '2', "Take"

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, )
    amount = models.FloatField()
    operation = models.CharField(choices=Month.choices, max_length=5)
    reason = models.CharField(max_length=255, )
    add_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
