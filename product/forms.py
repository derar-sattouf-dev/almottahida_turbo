from django import forms
from django.forms import ModelForm, HiddenInput

from product.models import *


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = "__all__"


class SellerForm(ModelForm):
    class Meta:
        model = Seller
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(SellerForm, self).__init__(*args, **kwargs)
        # super().__init__()
        self.fields['for_him'].widget = HiddenInput()
        self.fields['on_him'].widget = HiddenInput()


class InvoicePaymentForm(ModelForm):
    class Meta:
        model = InvoicePayment
        fields = "__all__"


class DailyBoxOperationForm(ModelForm):
    class Meta:
        model = DailyBoxOperation
        fields = "__all__"


class WorkerForm(ModelForm):
    class Meta:
        model = Worker
        fields = "__all__"


class CurrencyForm(ModelForm):
    class Meta:
        model = Currency
        fields = "__all__"


class QuantityTypeForm(ModelForm):
    class Meta:
        model = QuantityType
        fields = "__all__"


class MaterialForm(ModelForm):
    class Meta:
        model = Material
        fields = "__all__"


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
