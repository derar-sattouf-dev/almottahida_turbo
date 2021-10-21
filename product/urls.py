from django.urls import path

from product import views

urlpatterns = [
    path("category/", views.all_categories, name='category.all'),
    path("seller/", views.all_sellers, name='seller.all'),
    path("seller/<int:pk>/add_payment", views.add_seller_payment, name='seller.add_payment'),
    path("worker/", views.all_workers, name='worker.all'),
    path("box/", views.daily_box, name='box.daily'),
    path("quantity_types/", views.all_quantity_types, name='quantity_type.all'),
    path("currency/", views.all_currencies, name='currency.all'),
    path("material/", views.all_materials, name='material.all'),
    path("invoice/add", views.add_invoice, name='invoice.add'),
    path("invoice/<int:pk>/", views.view_invoice, name='invoice.view'),
    path("invoice/seller/<int:pk>/", views.seller_invoices, name='invoice.seller.view'),
    path("invoice/last", views.view_invoice_last, name='invoice.view.last'),
    path("invoice/all", views.all_invoices, name='invoice.all'),
    path("product/add/", views.add_product, name='product.add'),
    path("product/<int:pk>/edit", views.edit_product, name='product.edit'),
    path("product/autocomplete/", views.product_autocomplete, name='product.autocomplete'),
    path("product/get_currencies/", views.get_currencies, name='product.get_currencies'),
    path("product/get_sellers/", views.get_sellers, name='product.get_sellers'),
    path("product/get_workers/", views.get_workers, name='product.get_workers'),
    path("product/get_quantity_types/", views.get_quantity_types, name='product.get_quantity_types'),
    path("", views.all_products, name='product.all'),
]
