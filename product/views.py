import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from product.forms import *
from product.models import *
from turbo.settings import LOGIN_URL


# Categories
@login_required(login_url=LOGIN_URL)
def all_categories(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = request.POST.get("method").lower()
        if method == "post":
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Category added successfully.')
                return redirect("category.all")
        elif method == "delete":
            category_id = request.POST.get("category_id")
            Category.objects.get(pk=category_id).delete()
            messages.add_message(request, messages.WARNING, 'Category deleted successfully.')
            return redirect("category.all")
        elif method == "put":
            category_id = request.POST.get("category_id")
            category_name = request.POST.get("name")
            category_desc = request.POST.get("desc")
            category_exists = Category.objects.filter(name=category_name).exclude(pk=category_id)
            if not category_exists:
                category = Category.objects.get(pk=category_id)
                category.name = category_name
                category.desc = category_desc
                category.save()
                messages.add_message(request, messages.SUCCESS, 'Category updated successfully.')
            else:
                messages.add_message(request, messages.WARNING, 'Category data exists')

            return redirect("category.all")
            # Get method
    else:
        form = CategoryForm()
    categories = Category.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(categories, 15)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    return render(request, 'category/all.html', {'categories': categories, "form": form})


# Sellers
@login_required(login_url=LOGIN_URL)
def all_sellers(request):
    # post method
    if request.method == 'POST':
        method = request.POST.get("method").lower()
        if method == "post":
            form = SellerForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Seller added successfully.')
                return redirect("seller.all")
        elif method == "delete":
            seller_id = request.POST.get("seller_id")
            Seller.objects.get(pk=seller_id).delete()
            messages.add_message(request, messages.WARNING, 'Seller deleted successfully.')
            return redirect("seller.all")
        elif method == "put":
            seller_id = request.POST.get("seller_id")
            seller_name = request.POST.get("name")
            seller_phone = request.POST.get("phone")
            seller_address = request.POST.get("address")
            seller_exists = Seller.objects.filter(name=seller_name).exclude(pk=seller_id)
            if not seller_exists:
                seller = Seller.objects.get(pk=seller_id)
                seller.name = seller_name
                seller.phone = seller_phone
                seller.address = seller_address
                seller.save()
                messages.add_message(request, messages.SUCCESS, 'Seller updated successfully.')
            else:
                messages.add_message(request, messages.WARNING, 'Seller data exists')

            return redirect("seller.all")
    # Get method
    else:
        form = SellerForm()
    sellers = Seller.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(sellers, 15)
    try:
        sellers = paginator.page(page)
    except PageNotAnInteger:
        sellers = paginator.page(1)
    except EmptyPage:
        sellers = paginator.page(paginator.num_pages)

    return render(request, 'seller/all.html', {'sellers': sellers, "form": form})


@login_required(login_url=LOGIN_URL)
def add_seller_payment(request, pk):
    form = InvoicePaymentForm(request.POST or None)
    if form.is_valid():
        form.save()
    invoices = Invoice.objects.filter(seller_id=pk)
    payments = InvoicePayment.objects.filter(seller_id=pk)
    seller = Seller.objects.get(pk=pk)
    return render(request, "seller/add_payment.html",
                  {"form": form, "invoices": invoices, "payments": payments, "seller": seller})


@login_required(login_url=LOGIN_URL)
def daily_box(request):
    # form = DailyBoxOperationForm(request.POST or None)
    # if form.is_valid():
    #     form.save()
    # today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    # today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    # ops = DailyBoxOperation.objects.filter(add_date__range=(today_min, today_max))
    # return render(request, "box/daily_box.html",
    #               {"form": form, "ops": ops})
    pass

# Workers
@login_required(login_url=LOGIN_URL)
def all_workers(request):
    # post method
    if request.method == 'POST':
        method = request.POST.get("method").lower()
        if method == "post":
            form = WorkerForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Worker added successfully.')
                return redirect("worker.all")
        elif method == "delete":
            worker_id = request.POST.get("worker_id")
            Worker.objects.get(pk=worker_id).delete()
            messages.add_message(request, messages.WARNING, 'Worker deleted successfully.')
            return redirect("worker.all")
        elif method == "put":
            worker_id = request.POST.get("worker_id")
            worker_name = request.POST.get("name")
            worker_phone = request.POST.get("phone")
            worker_exists = Worker.objects.filter(name=worker_name).exclude(pk=worker_id)
            if not worker_exists:
                worker = Worker.objects.get(pk=worker_id)
                worker.name = worker_name
                worker.phone = worker_phone
                worker.save()
                messages.add_message(request, messages.SUCCESS, 'Worker updated successfully.')
            else:
                messages.add_message(request, messages.WARNING, 'Worker data exists')

            return redirect("worker.all")
    # Get method
    else:
        form = WorkerForm()
    workers = Worker.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(workers, 15)
    try:
        workers = paginator.page(page)
    except PageNotAnInteger:
        workers = paginator.page(1)
    except EmptyPage:
        workers = paginator.page(paginator.num_pages)

    return render(request, 'worker/all.html', {'workers': workers, "form": form})


@login_required(login_url=LOGIN_URL)
def all_quantity_types(request):
    if request.method == 'POST':
        method = request.POST.get("method").lower()
        if method == "post":
            form = QuantityTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Quantity Type added successfully.')
                return redirect("quantity_type.all")
        elif method == "delete":
            quantity_type_id = request.POST.get("quantity_type_id")
            QuantityType.objects.get(pk=quantity_type_id).delete()
            messages.add_message(request, messages.WARNING, 'Quantity Type deleted successfully.')
            return redirect("quantity_type.all")
        elif method == "put":
            quantity_type_id = request.POST.get("quantity_type_id")
            quantity_type_name = request.POST.get("name")
            quantity_type_value = request.POST.get("value")
            quantity_type_exists = QuantityType.objects.filter(name=quantity_type_name).exclude(pk=quantity_type_id)
            if not quantity_type_exists:
                quantity_type = QuantityType.objects.get(pk=quantity_type_id)
                quantity_type.name = quantity_type_name
                quantity_type.value = quantity_type_value
                quantity_type.save()
                messages.add_message(request, messages.SUCCESS, 'Quantity Type updated successfully.')
            else:
                messages.add_message(request, messages.WARNING, 'Quantity Type data exists')

            return redirect("quantity_type.all")
            # Get method
    else:
        form = QuantityTypeForm()
        quantity_types = QuantityType.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(quantity_types, 15)
    try:
        quantity_types = paginator.page(page)
    except PageNotAnInteger:
        quantity_types = paginator.page(1)
    except EmptyPage:
        quantity_types = paginator.page(paginator.num_pages)
    return render(request, 'quantity_type/all.html', {'quantity_types': quantity_types, "form": form})


# Currencies
@login_required(login_url=LOGIN_URL)
def all_currencies(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = request.POST.get("method").lower()
        if method == "post":
            form = CurrencyForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Currency added successfully.')
                return redirect("currency.all")
        elif method == "delete":
            currency_id = request.POST.get("currency_id")
            Currency.objects.get(pk=currency_id).delete()
            messages.add_message(request, messages.WARNING, 'Currency deleted successfully.')
            return redirect("currency.all")
        elif method == "put":
            currency_id = request.POST.get("currency_id")
            currency_name = request.POST.get("name")
            currency_value = request.POST.get("value")
            currency_rate = request.POST.get("rate")
            currency_exists = Currency.objects.filter(name=currency_name).exclude(pk=currency_id)
            if not currency_exists:
                currency = Currency.objects.get(pk=currency_id)
                currency.name = currency_name
                currency.value = currency_value
                currency.rate = currency_rate
                currency.save()
                messages.add_message(request, messages.SUCCESS, 'Currency updated successfully.')
            else:
                messages.add_message(request, messages.WARNING, 'Currency data exists')

            return redirect("currency.all")
            # Get method
    else:
        form = CurrencyForm()
    currencies = Currency.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(currencies, 15)
    try:
        currencies = paginator.page(page)
    except PageNotAnInteger:
        currencies = paginator.page(1)
    except EmptyPage:
        currencies = paginator.page(paginator.num_pages)

    return render(request, 'currency/all.html', {'currencies': currencies, "form": form})


# Materials
@login_required(login_url=LOGIN_URL)
def all_materials(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        method = request.POST.get("method").lower()
        if method == "post":
            form = MaterialForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Material added successfully.')
                return redirect("material.all")
        elif method == "delete":
            material_id = request.POST.get("material_id")
            Material.objects.get(pk=material_id).delete()
            messages.add_message(request, messages.WARNING, 'Material deleted successfully.')
            return redirect("material.all")
        elif method == "put":
            material_id = request.POST.get("material_id")
            material_name = request.POST.get("name")
            material_desc = request.POST.get("desc")
            material_exists = Material.objects.filter(name=material_name).exclude(pk=material_id)
            if not material_exists:
                material = Material.objects.get(pk=material_id)
                material.name = material_name
                material.desc = material_desc
                material.save()
                messages.add_message(request, messages.SUCCESS, 'Material updated successfully.')
            else:
                messages.add_message(request, messages.WARNING, 'Material data exists')

            return redirect("material.all")
            # Get method
    else:
        form = MaterialForm()
    materials = Material.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(materials, 15)
    try:
        materials = paginator.page(page)
    except PageNotAnInteger:
        materials = paginator.page(1)
    except EmptyPage:
        materials = paginator.page(paginator.num_pages)

    return render(request, 'material/all.html', {'materials': materials, "form": form})


@login_required(login_url=LOGIN_URL)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Product added successfully.')
            return redirect("product.all")
    else:
        form = ProductForm()
        return render(request, 'product/add.html', {"form": form})


@login_required(login_url=LOGIN_URL)
def edit_product(request, pk):
    product = Product.objects.get(pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
    return render(request, 'product/edit.html', {"form": form, "product": product})


@login_required(login_url=LOGIN_URL)
def all_products(request):
    products = Product.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 15)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(request, "product/all.html", {"products": products})


@login_required(login_url=LOGIN_URL)
def view_invoice(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    products = InvoiceProduct.objects.filter(invoice_id=pk)
    return render(request, "invoice/view.html", {"invoice": invoice, "products": products})


@login_required(login_url=LOGIN_URL)
def add_invoice(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        invoice = Invoice()

        cur = Currency.objects.get(pk=data["activeCurrency"])
        invoice.currency = cur
        cur.value = cur.value + float(data["payed"])
        cur.save()

        se = Seller.objects.get(pk=data["activeSeller"])
        invoice.seller = se

        wo = Worker.objects.get(pk=data["activeWorker"])
        invoice.worker = wo

        invoice.total = data["total"]
        invoice.discount = data["discount"]
        invoice.dept = data["dept"]
        invoice.payed = data["payed"]
        invoice.paydate = data["paydate"]

        # invoice.expected_earn = Currency.objects.get(pk=data["activeCurrency"])
        invoice.save()

        for product in data["activeProducts"]:
            invoiceProduct = InvoiceProduct()
            invoiceProduct.invoice_id = invoice.pk
            invoiceProduct.product_id = product["pk"]
            invoiceProduct.total = product["total"]
            invoiceProduct.quantity = product["quantity"]
            invoiceProduct.piece_price = product["price"]
            invoiceProduct.extra_quantity = 0
            invoiceProduct.quantity_type_id = 1
            invoiceProduct.save()
            realProduct = Product.objects.get(pk=product["pk"])
            flval = float(product["quantity"])
            realProduct.quantity = realProduct.quantity - flval
            realProduct.save()
            resp = {"pk": invoice.pk}
        return JsonResponse(resp)
    else:
        return render(request, "invoice/add.html")


def product_autocomplete(request):
    query = request.POST.get("query")
    if len(query) > 2:
        products = Product.objects.filter(
            Q(name__contains=query) |
            Q(material__name__contains=query) |
            Q(identifier__contains=query) |
            Q(barcode__contains=query)
        )

        products = serializers.serialize("json", products)
        result = {"result": products}
        return JsonResponse(result)


def get_currencies(request):
    result = Currency.objects.all()
    result = serializers.serialize("json", result)
    result = {"result": result}
    return JsonResponse(result)


def get_sellers(request):
    result = Seller.objects.all()
    result = serializers.serialize("json", result)
    result = {"result": result}
    return JsonResponse(result)


def get_workers(request):
    result = Worker.objects.all()
    result = serializers.serialize("json", result)
    result = {"result": result}
    return JsonResponse(result)


def get_quantity_types(request):
    result = QuantityType.objects.all()
    result = serializers.serialize("json", result)
    result = {"result": result}
    return JsonResponse(result)


@login_required(login_url=LOGIN_URL)
def view_invoice_last(request):
    invoice = Invoice.objects.last()
    return redirect(reverse("invoice.view", args=[invoice.pk]))


@login_required(login_url=LOGIN_URL)
def all_invoices(request):
    invoices = Invoice.objects.all()
    return render(request, "invoice/all.html", {"invoices": invoices})


@login_required(login_url=LOGIN_URL)
def seller_invoices(request, pk):
    invoices = Invoice.objects.filter(seller=pk)
    return render(request, "invoice/all.html", {"invoices": invoices})
