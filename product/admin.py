from django.contrib import admin

# Register your models here.
from product.models import *

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Seller)
admin.site.register(QuantityType)
admin.site.register(Material)
admin.site.register(Currency)
admin.site.register(Invoice)
admin.site.register(InvoiceProduct)
