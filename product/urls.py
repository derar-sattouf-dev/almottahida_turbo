from django.urls import path

from product import views

urlpatterns = [
    path("category/", views.all_categories, name='category.all'),
    path("category/<int:pk>/products", views.category_products, name='category.products'),
    path("seller/", views.all_sellers, name='seller.all'),
    path("seller/discount", views.seller_discount, name='seller.discount'),
    path("seller/<int:pk>/add_payment", views.add_seller_payment, name='seller.add_payment'),
    path("seller/remote_invoices", views.remote_seller_invoices, name='seller.remote_invoices'),
    path("seller/remote_payments", views.remote_seller_payments, name='seller.remote_payments'),
    path("worker/", views.all_workers, name='worker.all'),
    path("box/", views.daily_box, name='box.daily'),
    path("quantity_types/", views.all_quantity_types, name='quantity_type.all'),
    path("currency/", views.all_currencies, name='currency.all'),
    path("material/", views.all_materials, name='material.all'),
    path("invoice/add", views.add_invoice, name='invoice.add'),
    path("payment/all", views.all_payments, name='payment.all'),
    path("invoice/<int:pk>/", views.view_invoice, name='invoice.view'),
    path("invoice/return", views.returned_invoices, name='invoice.returned'),
    path("invoice/<int:pk>/return", views.return_invoice, name='invoice.return'),
    path("invoice/<int:pk>/edit", views.edit_invoice, name='invoice.edit'),
    path("invoice/seller/<int:pk>/", views.seller_invoices, name='invoice.seller.view'),
    path("invoice/last", views.view_invoice_last, name='invoice.view.last'),
    path("invoice/all", views.all_invoices, name='invoice.all'),
    path("product/add/", views.add_product, name='product.add'),
    path("product/offer/", views.offer, name='product.offer'),
    path("product/all_json/", views.get_all_products, name='product.all_json'),
    path("product/all_materials/", views.get_all_materials, name='product.all_materials'),
    path("product/<int:pk>/edit", views.edit_product, name='product.edit'),
    path("product/autocomplete/", views.product_autocomplete, name='product.autocomplete'),
    path("product/get_currencies/", views.get_currencies, name='product.get_currencies'),
    path("product/get_sellers/", views.get_sellers, name='product.get_sellers'),
    path("product/get_workers/", views.get_workers, name='product.get_workers'),
    path("product/report/<int:pk>/", views.product_report, name='product.report'),
    path("product/get_invoice_products/<int:pk>", views.get_invoice_products, name='product.get_invoice_products'),
    path("product/get_quantity_types/", views.get_quantity_types, name='product.get_quantity_types'),
    path("", views.all_products, name='product.all'),
    path("rawad/", views.rawad, name='product.rawad'),
    path("show/", views.show, name='product.show'),
    path("reports/", views.all_reports, name='reports.all'),
    path("exports/", views.all_exports, name='all_exports'),
]
