import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
import json
# import qrcode
# import qrcode.image.svg
# from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from segno import helpers
from product.forms import *
from product.models import *
from turbo.settings import LOGIN_URL
from django.core import serializers


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
            else:
                return HttpResponse(form.errors)
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
    if "search" in request.GET:
        sellers = Seller.objects.filter(name__icontains=request.GET["search"])
    else:
        sellers = Seller.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(sellers, 100)
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
        amount = form.cleaned_data["amount"]
        op = form.cleaned_data["operation"]
        currency = Currency.objects.get(name__exact=form.cleaned_data["currency"])
        currency_value = currency.value
        if op == "Give":
            currency_value -= amount
        else:
            currency_value += amount
        currency.value = currency_value
        currency.save()
    if request.GET.get("from") and request.GET.get("to"):
        seller = Seller.objects.get(pk=pk)
        _from = request.GET.get("from")
        _to = request.GET.get("to")
        #
        apt = 0
        apg = 0
        aip = 0
        ais = 0

        #
        invoices = Invoice.objects.filter(seller_id=pk, date_added__range=(_from, _to))
        payments = InvoicePayment.objects.filter(seller_id=pk, add_date__range=(_from, _to))

        discounts = SellerDiscount.objects.filter(seller=seller)
        total_invoices = 0
        total_payments = 0
        total_discounts = 0
        for invoice in invoices:
            invoice.discount = float(format(invoice.discount, ".2f"))
            if invoice.type == "Sale":
                total_invoices += (invoice.total - invoice.discount)
                ais += (invoice.total - invoice.discount)

            else:
                total_invoices -= (invoice.total - invoice.discount)
                if invoice.type == "Purchase":
                    aip += (invoice.total - invoice.discount)

        for payment in payments:
            if payment.operation == "Give":
                total_payments -= payment.amount / payment.rate
                apg += payment.amount / payment.rate

            else:
                total_payments += payment.amount / payment.rate
                apt += payment.amount / payment.rate

        for discount in discounts:
            total_discounts += discount.amount

        invoices_before_from = Invoice.objects.filter(seller_id=pk,
                                                      date_added__range=(datetime.date(2000, 2, 2), _from))
        payments_before_from = InvoicePayment.objects.filter(seller_id=pk,
                                                             add_date__range=(datetime.date(2000, 2, 2), _from))
        total_old_invoices = 0
        total_old_payments = 0
        for invoice in invoices_before_from:
            invoice.discount = float(format(invoice.discount, ".2f"))
            if invoice.type == "Sale":
                total_old_invoices += (invoice.total - invoice.discount)
            else:
                total_old_invoices -= (invoice.total - invoice.discount)
        for payment in payments_before_from:
            if payment.operation == "Give":
                total_old_payments -= payment.amount / payment.rate
            else:
                total_old_payments += payment.amount / payment.rate
        seller.old_account = total_old_invoices - total_old_payments + seller.old_account
        total = total_invoices - total_payments + seller.old_account - total_discounts
        seller.old_account = format(seller.old_account, ".2f")
        total = format(total, ".2f")
    else:
        apt = 0
        apg = 0
        aip = 0
        ais = 0
        invoices = Invoice.objects.filter(seller_id=pk)
        payments = InvoicePayment.objects.filter(seller_id=pk)
        total_invoices = 0
        for invoice in invoices:
            invoice.discount = float(format(invoice.discount, ".2f"))
            if invoice.type == "Sale":
                total_invoices += (invoice.total - invoice.discount)
                ais += (invoice.total - invoice.discount)

            else:
                if invoice.type == "Purchase":
                    aip += (invoice.total - invoice.discount)

                total_invoices -= (invoice.total - invoice.discount)
        total_payments = 0
        for payment in payments:
            if payment.operation == "Give":
                total_payments -= payment.amount / payment.rate
                apg += payment.amount / payment.rate
            else:
                total_payments += payment.amount / payment.rate
                apt += payment.amount / payment.rate
        seller = Seller.objects.get(pk=pk)
        total_discounts = 0
        discounts = SellerDiscount.objects.filter(seller=seller)
        for discount in discounts:
            total_discounts += discount.amount
        total = total_invoices - total_payments + seller.old_account - total_discounts
        total = format(total, ".2f")

    return render(request, "seller/add_payment.html",
                  {"form": form, "invoices": invoices, "payments": payments, "discounts": discounts, "seller": seller,
                   "total_invoices": total_invoices, "total_payments": total_payments, "total": total,
                   "apt": apt,
                   "apg": apg,
                   "aip": aip,
                   "ais": ais,
                   })


@login_required(login_url=LOGIN_URL)
def daily_box(request):
    form = DailyBoxOperationForm(request.POST or None)
    if form.is_valid():
        op = form.cleaned_data["operation"]
        amount = form.cleaned_data["amount"]
        currency = Currency.objects.get(name__exact=form.cleaned_data["currency"])
        currency_value = currency.value
        if op == "Give":
            currency_value -= amount
        else:
            currency_value += amount
        currency.value = currency_value
        currency.save()
        form.save()

    if request.GET.get("from") is None:
        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        ops = DailyBoxOperation.objects.filter(add_date__range=(today_min, today_max)).order_by("-pk")
    else:
        _from = request.GET.get("from")
        _to = request.GET.get("to")
        ops = DailyBoxOperation.objects.filter(add_date__range=(_from, _to))
    return render(request, "box/daily_box.html",
                  {"form": form, "ops": ops})
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
    for c in currencies:
        c.value = format(c.value, ".2f")
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
            return HttpResponse(form.errors)
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
    if "search" in request.GET:
        query = request.GET["search"]
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(material__name__icontains=query))
    else:
        products = Product.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(products, 100)
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
    for p in products:
        p.total_pices = str(float(float(p.quantity * p.quantity_type.value) + float(
            p.extra_quantity)) * p.product.weight_value)

        p.total_pices = format(float(p.total_pices), ".2f")
        p.total = format(float(p.total), ".2f")

        p.total_pices += p.product.weight

        p.total_pices_count = str(
            float(float(p.quantity * p.quantity_type.value) + float(p.extra_quantity))) + " Pieces"
    invoice.total -= invoice.discount
    invoice.total = format(invoice.total, ".2f")
    invoice.discount = format(invoice.discount, ".2f")
    qrcode = helpers.make_mecard(
        country="Tripoli",
        name='Almottahida',
        phone=("+96181444944", "+96181444934", "+96181444954", "+96181444964", "+96181444974", "+96181444984"),
        email='contact@almottahida.org',
        url=['almottahida.org'])
    return render(request, "invoice/view.html", {"invoice": invoice, "products": products, "qr": qrcode.svg_inline()})


@login_required(login_url=LOGIN_URL)
def add_invoice(request):
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        invoice = Invoice()
        # type
        invoice.type = data["activeType"]
        se = Seller.objects.get(pk=data["activeSeller"])
        invoice.seller = se
        # worker
        wo = Worker.objects.get(pk=data["activeWorker"])
        invoice.worker = wo
        invoice.total = data["total"]
        invoice.discount = data["discount"]
        invoice.payed = 0
        invoice.remaining = data["total"]
        invoice.save()
        for product in data["activeProducts"]:
            invoiceProduct = InvoiceProduct()
            invoiceProduct.invoice_id = invoice.pk
            invoiceProduct.product_id = product["pk"]
            invoiceProduct.total = product["total"]
            invoiceProduct.quantity = product["quantity"]
            invoiceProduct.piece_price = product["price"]
            invoiceProduct.extra_quantity = product["extra_quantity"]
            active_quantity_type = QuantityType.objects.get(pk=product["quantity_type"]["pk"])
            invoiceProduct.quantity_type = active_quantity_type
            invoiceProduct.save()
            realProduct = Product.objects.get(pk=product["pk"])
            flval = float(product["quantity"])
            if invoice.type == "Sale":
                boc_val = float(active_quantity_type.value)
                current_t = float(realProduct.quantity)
                current_e = float(realProduct.extra_quantity)
                sold_t = product["quantity"]
                sold_e = product["extra_quantity"]
                total_peer_pice_in_stock = float(boc_val) * float(current_t) + float(current_e)
                total_peer_pice_to_sale = float(boc_val) * float(sold_t) + float(sold_e)
                will_remian_by_pice = float(total_peer_pice_in_stock) - float(total_peer_pice_to_sale)
                will_be_e = float(will_remian_by_pice % boc_val)
                will_be_t = float(float((will_remian_by_pice - will_be_e)) / float(boc_val))
                realProduct.quantity = float(will_be_t)
                realProduct.extra_quantity = float(will_be_e)
            if invoice.type == "Purchase":
                boc_val = float(active_quantity_type.value)
                current_t = float(realProduct.quantity)
                current_e = float(realProduct.extra_quantity)
                purchased_t = product["quantity"]
                purchased_e = product["extra_quantity"]
                total_peer_pice_in_stock = float(boc_val) * float(current_t) + float(current_e)
                total_peer_pice_to_purhcase = float(boc_val) * float(purchased_t) + float(purchased_e)
                will_remian_by_pice = float(total_peer_pice_in_stock) + float(total_peer_pice_to_purhcase)
                will_be_e = float(will_remian_by_pice % boc_val)
                will_be_t = float(float((will_remian_by_pice - will_be_e)) / float(boc_val))
                realProduct.quantity = float(will_be_t)
                realProduct.extra_quantity = float(will_be_e)
            realProduct.save()
            resp = {"pk": invoice.pk}
        return JsonResponse(resp)
    else:
        return render(request, "invoice/add.html")


def product_autocomplete(request):
    query = request.POST.get("query")
    if len(query) > 2:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(material__name__icontains=query) |
            Q(identifier__icontains=query) |
            Q(barcode__icontains=query)
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
    invoices = Invoice.objects.all().order_by("-pk")
    return render(request, "invoice/all.html", {"invoices": invoices})


@login_required(login_url=LOGIN_URL)
def seller_invoices(request, pk):
    invoices = Invoice.objects.filter(seller=pk)
    return render(request, "invoice/all.html", {"invoices": invoices})


@login_required(login_url=LOGIN_URL)
def rawad(request):
    if "search" in request.GET:
        products = Product.objects.filter(name__icontains=request.GET["search"])
    else:
        products = Product.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(products, 15)
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

    for product in products:
        product.weight_value = (float(product.quantity * product.quantity_type.value) + float(
            product.extra_quantity)) * float(product.weight_value)
    return render(request, "product/rawad.html", {"products": products})


def show(request):
    products = Product.objects.all()
    return render(request, "product/show.html", {"products": products})


@login_required(login_url=LOGIN_URL)
def edit_invoice(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.save()
    return render(request, 'invoice/edit.html', {"form": form, "invoice": invoice})


@login_required(login_url=LOGIN_URL)
def returned_invoices(request):
    returned = Invoice.objects.filter(type="Return")
    return render(request, "invoice/all.html", {"invoices": returned})


@login_required(login_url=LOGIN_URL)
def return_invoice(request, pk):
    if request.method == "GET":
        invoice = Invoice.objects.get(pk=pk)
        context = {
            "invoice": invoice,
        }
        return render(request, "invoice/return.html", context)
    if request.method == "POST":
        data = json.loads(request.POST.get("data"))
        old_invoice = Invoice.objects.get(pk=pk)
        old_type = old_invoice.type
        invoiceProducts = data["products"]
        invoice = Invoice()
        se = Seller.objects.get(pk=data["seller"])
        wo = Worker.objects.get(pk=data["worker"])

        invoice.type = "Return"
        invoice.seller = se
        invoice.worker = wo
        invoice.total = 0
        for invoiceProduct in invoiceProducts:
            invoice.total += invoiceProduct["total"]
            ip = InvoiceProduct()
            ip.quantity = invoiceProduct["quantity"]
            ip.extra_quantity = invoiceProduct["extra_quantity"]
            ip.total = invoiceProduct["total"]
            ip.piece_price = invoiceProduct["piece_price"]
            ip.product_id = invoiceProduct["product"]
            ip.quantity_type = QuantityType.objects.get(pk=invoiceProduct["quantity_type"])
            ip.invoice = Invoice.objects.last()
            ip.save()
            # Parent product updates
            product = Product.objects.get(pk=invoiceProduct["product"])
            if old_type == "Sale":
                product.quantity = product.quantity + float(invoiceProduct["quantity"])
                product.extra_quantity = product.extra_quantity + float(invoiceProduct["extra_quantity"])
            if old_type == "Purchase":
                product.quantity = product.quantity - float(invoiceProduct["quantity"])
                product.extra_quantity = product.extra_quantity - float(invoiceProduct["extra_quantity"])
            product.save()
        if old_type == "Purchase":
            invoice.total = -invoice.total
        invoice.save()
        return HttpResponse(invoice.total)


def get_invoice_products(request, pk):
    products = []
    invoice_products = InvoiceProduct.objects.filter(invoice=pk)
    for invoice_product in invoice_products:
        product = Product.objects.get(pk=invoice_product.product.pk)
        products.append(product)
    products = serializers.serialize("json", products)
    invoice_products = serializers.serialize("json", invoice_products)
    response = {
        "invoice_products": invoice_products,
        "products": products
    }
    return JsonResponse(response)


@login_required(login_url=LOGIN_URL)
def all_payments(request):
    all_sellers = Seller.objects.all()
    blocks = []
    for seller in all_sellers:
        invoices = Invoice.objects.filter(seller=seller)
        payments = InvoicePayment.objects.filter(seller=seller)

        total_invoices = 0
        for invoice in invoices:
            if invoice.type == "Sale":
                total_invoices += (invoice.total - invoice.discount)
            else:
                total_invoices -= (invoice.total - invoice.discount)

        total_payments = 0
        for payment in payments:
            if payment.operation == "Give":
                total_payments -= payment.amount / payment.rate
            else:
                total_payments += payment.amount / payment.rate

        account = total_invoices - total_payments + seller.old_account
        if account != 0:
            to_add = {
                "seller": seller,
                "account": format(account, ".2f")
            }
            blocks.append(to_add)
    return render(request, "invoice/mustpay.html", {"blocks": blocks})


@login_required(login_url=LOGIN_URL)
def offer(request):
    return render(request, "product/offer.html")


def get_all_products(request):
    result = Product.objects.all()
    result = serializers.serialize("json", result)
    result = {"result": result}
    return JsonResponse(result)


def get_all_materials(request):
    result = Material.objects.all()
    result = serializers.serialize("json", result)
    result = {"result": result}
    return JsonResponse(result)


def category_products(request, pk):
    products = Product.objects.filter(category_id=pk)
    return render(request, "category/products.html", {"products": products})


@login_required(login_url=LOGIN_URL)
def all_reports(request):
    context = {}
    total_stock_price = 0
    total_sale_price = 0
    total_depts = 0
    total_must_pay = 0
    total_saled = 0
    total_earned = 0
    total_box_takes = 0
    all_products = Product.objects.all()
    all_invoices = Invoice.objects.filter(type="Sale")
    all_invoice_products = InvoiceProduct.objects.all()
    all_sellers = Seller.objects.all()
    all_box_operations = DailyBoxOperation.objects.all()

    for invoice in all_invoices:
        total_saled += invoice.total - invoice.discount

    for product in all_invoice_products:
        total_price = product.product.stock_price * (
                (product.quantity_type.value * product.quantity) + product.extra_quantity)
        total_sales = product.total
        final_number = total_sales - total_price
        total_earned += final_number
        # Products
    for product in all_products:
        stock_price = product.stock_price
        price = product.price
        quantity_in_pices = (product.quantity_type.value * product.quantity) + product.extra_quantity
        total_stock_price += quantity_in_pices * stock_price
        total_sale_price += quantity_in_pices * price

    for seller in all_sellers:
        invoices = Invoice.objects.filter(seller=seller)
        payments = InvoicePayment.objects.filter(seller=seller)

        total_invoices = 0
        for invoice in invoices:
            if invoice.type == "Sale":
                total_invoices += (invoice.total - invoice.discount)
            else:
                total_invoices -= (invoice.total - invoice.discount)

        total_payments = 0
        for payment in payments:
            if payment.operation == "Give":
                total_payments -= payment.amount / payment.rate
            else:
                total_payments += payment.amount / payment.rate

        account = total_invoices - total_payments + seller.old_account
        if account > 0:
            total_depts += account
        if account < 0:
            total_must_pay += account

    context["total_stock_price"] = format(total_stock_price, ".2f")
    context["total_sale_price"] = format(total_sale_price, ".2f")
    context["total_depts"] = format(total_depts, ".2f")
    context["total_must_pay"] = format(total_must_pay, ".2f")
    context["total_saled"] = format(total_saled, ".2f")
    context["total_earned"] = format(total_earned, ".2f")
    context["total_box_takes"] = format(total_box_takes, ".2f")
    return render(request, "reports.html", context)


@csrf_exempt
def remote_seller_invoices(request):
    invoices = Invoice.objects.filter(seller__name=request.POST.get("name"))
    for invoice in invoices:
        invoice.discount = float(format(invoice.discount, ".2f"))
    tmpJson = serializers.serialize("json", invoices)
    tmpObj = json.loads(tmpJson)
    return HttpResponse(json.dumps(tmpObj))


@csrf_exempt
def remote_seller_payments(request):
    payments = InvoicePayment.objects.filter(seller__name=request.POST.get("name"))
    for payment in payments:
        payment.amount = payment.amount / payment.rate
    tmpJson = serializers.serialize("json", payments)
    tmpObj = json.loads(tmpJson)
    return HttpResponse(json.dumps(tmpObj))


@login_required(login_url=LOGIN_URL)
def seller_discount(request):
    sellers = Seller.objects.all()
    if request.method == 'POST':
        form = SellerDiscountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Discount added successfully.')
            return redirect("invoice.all")
    else:
        form = SellerDiscountForm

    return render(request, "seller/discount.html", {'sellers': sellers, "form": form})


@login_required(login_url=LOGIN_URL)
def product_report(request, pk):
    product = Product.objects.get(pk=pk)

    si = Invoice.objects.filter(invoiceproduct__product=product, type__exact="Sale")
    pi = Invoice.objects.filter(invoiceproduct__product=product, type__exact="Purchase")
    return render(request, "product/product_report.html", {
        "si": si,
        "bproduct": product,
        "pi": pi,
    })
