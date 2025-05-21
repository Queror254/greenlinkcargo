from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.decorators import login_required
from .models import Shipment, Invoice, Payment
from setting_app.models import Rates
from clients.models import Client
from users.models import Business, Branch
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal


# render the clients ledger
class ClientLedgerView(DetailView):
    # initialize the model and the template
    model = Client
    template_name = 'shipments/client_ledger.html'
    
    # get the contex data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = Invoice.objects.filter(client=self.object).select_related('shipment')
        # calaculate total balance due across all invoices under said client
        # i think later on i can use the total_amount instead of balance_due
        total_balance_due = sum(invoice.balance_due for invoice in invoices)
        context['invoices'] = invoices
        context['total_owed'] = total_balance_due
        context['total_paid'] = Payment.objects.filter(
            invoice__client=self.object
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return context
 
# render an invoice details page
class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'shipments/invoice_detail.html'
    context_object_name = "invoice"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.object.payments.all()
        return context

# generate a downloadable invoice pdf
@login_required
def generate_invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    context = {
        'invoice': invoice,
        'payments': invoice.payments.all(),
        'business': invoice.business
    }
    
    html = render_to_string('invoices/invoice_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=invoice_{invoice.invoice_number}.pdf'
    
    pisa.CreatePDF(html, dest=response)
    return response

# update payment status logic
#@login_required
class UpdatePaymentStatusView(UpdateView):
    model = Invoice
    fields = ['payment_status']  # Make sure this matches your form field
    template_name = 'shipments/update_payment.html'
    
    def form_valid(self, form):
        # Get the form instance
        invoice = form.save(commit=False)
        
        # Handle payment recording if status is paid/partial
        if invoice.payment_status in ['paid', 'partial']:
            try:
                amount = float(self.request.POST.get('amount', 0))
                if amount > 0:
                    Payment.objects.create(
                        invoice=invoice,
                        amount=amount,
                        method=self.request.POST.get('payment_method', 'other'),
                        reference=self.request.POST.get('reference', ''),
                        notes=self.request.POST.get('notes', '')
                    )
            except (ValueError, TypeError):
                messages.error(self.request, 'Invalid payment amount')
                return self.form_invalid(form)
        
        # Save the invoice
        invoice.save()
        
        # Update payment status based on actual payments
        invoice.update_payment_status()
        
        messages.success(self.request, 'Payment status updated successfully')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('invoice_detail', kwargs={'pk': self.object.pk})

# generate a shipment receipt to be attached to shipment
@login_required   
def generate_shipment_receipt(request, shipment_id):
    shipment = Shipment.objects.get(id=shipment_id)
    domain = 'https://techmystique.pythonanywhere.com'
    
    context = {
        'shipment': shipment,
        'business': shipment.business,
        'now': timezone.now().strftime("%Y-%m-%d %H:%M"),
        'tracking_url': f"{domain}/shipments/track/shipment?tracking_number={shipment.tracking_number}/"
    }
    
    html_string = render_to_string('shipments/receipt.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=package_receipt_{shipment.tracking_number}.pdf'
    
    pisa_status = pisa.CreatePDF(
        html_string, 
        dest=response,
        encoding='UTF-8',
        pagesize=(3.5*72, 6*72)  # Smaller receipt size
    )
    
    if pisa_status.err:
        return HttpResponse('PDF generation error')
    return response

# update the shipment complete status true or false
@login_required
def mark_shipment_complete(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)

    if shipment.shipment_complete:
        messages.info(request, "Shipment is already marked as complete.")
    else:
        shipment.shipment_complete = True
        shipment.status = "delivered"  # Optional: update status
        shipment.save()
        messages.success(request, "Shipment marked as complete.")

    return redirect('shipment_detail', pk=shipment.pk)  # or wherever you want to redirect

# fetch & render a shipment list
@login_required
def getall_shipment(request):
    shipments = Shipment.objects.all()
     # Ensure only the client who created the shipment or an admin/staff can view it
    if not request.user.is_authenticated:
        return render(request, '403.html', {'error': 'You are not authorized to view this shipment'})
    return render(request, 'shipments/shipment_list.html', {'shipments': shipments})

# create shipment    
@login_required
def createshipment_view(request):
    user = request.user
    
    # Initialize variables
    clients = Client.objects.none()
    business = None

    if user.role == 'admin':
        # Admin can see all active clients in their business
        business = get_object_or_404(Business, owner=user)
        clients = Client.objects.filter(business=business)
        
    else:
        # Staff can only see clients from their branch
        branch = user.branch
        business = branch.business
        clients = Client.objects.filter(branch=branch)
        
    
    if request.method == 'POST':
        client_id = request.POST.get('client')
        # chack if any client-id was provided in the POST request
        if client_id:
            client = get_object_or_404(Client, id=client_id)
        else: #if no then we create a new client :
            client_name = request.POST.get('client_name')
            client_email = request.POST.get('client_email')
            client_phone = request.POST.get('client_phone')
            client_address = request.POST.get('client_address', '')
            client_city = request.POST.get('client_city', '')
            client_postalcode = request.POST.get('client_postalcode', '')

            client, created = Client.objects.get_or_create(
                email=client_email,
                defaults={
                    'name': client_name,
                    'phone': client_phone,
                    'address': client_address,
                    'city': client_city,
                    'postalcode': client_postalcode,
                }
            )
        
        shipment_type = request.POST.get('shipment_type')
        shipment_quantity = request.POST.get('quantity');
        #shipment_cost = request.POST.get('shipment_cost')
        weight = request.POST.get('weight')
        volume = request.POST.get('volume')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        r_name = request.POST.get('recepient_name', '')
        r_phone = request.POST.get('recepient_phone', '')
        tocity = request.POST.get('city')
        toaddress = request.POST.get('address')
        status = request.POST.get('status', '')
        seawaybill = request.POST.get('seawaybill', '')
        airwaybill = request.POST.get('airwaybill', '')

        if shipment_type == 'air':
            if not (shipment_type and weight and origin and destination):
                return render(request, 'shipments/create_shipment.html', {
                    'clients': clients,
                    'error': 'For air shipments, weight, origin, and destination are required.'
                })
            try:
                weight = float(weight)
                Airwaybill = airwaybill
            except ValueError:
                return render(request, 'shipments/create_shipment.html', {
                    'clients': clients,
                    'error': 'Weight must be a valid number.'
                })
            volume = 0.0  # Default volume for air shipments
            Seawaybill = 'N/A'

        elif shipment_type == 'sea':
            if not (shipment_type and volume and origin and destination):
                return render(request, 'shipments/create_shipment.html', {
                    'clients': clients,
                    'error': 'For sea shipments, volume, origin, and destination are required.'
                })
            try:
                volume = float(volume)
                Seawaybill = seawaybill
            except ValueError:
                return render(request, 'shipments/create_shipment.html', {
                    'clients': clients,
                    'error': 'Volume must be a valid number.'
                })
            weight = 0.0  # Default weight for sea shipments
            Airwaybill = "N/A"
        else:
            return render(request, 'shipments/create_shipment.html', {
                'clients': clients,
                'error': 'Invalid shipment type.'
            })

        # Fetch rate from the Rates model
        rate = Rates.objects.first()  # Assuming there's only one rate record
        if not rate:
            return render(request, 'shipments/create_shipment.html', {
                'clients': clients,
                'error': 'No rate configuration found. Please set up rates in the system.'
            })

        # Calculate shipment cost
        #if shipment_type == 'air':
        #    shipment_cost = Decimal(str(weight)) * rate.weight_rate
        #elif shipment_type == 'sea':
        #    shipment_cost = Decimal(str(volume)) * rate.cbm_rate
        #else:
        #    shipment_cost = 0.0  # Default case (should not happen)

        # Create the shipment
        shipment = Shipment.objects.create(
            business=business,
            client=client,
            shipment_type=shipment_type,
            airwaybill=Airwaybill,
            seawaybill=Seawaybill,
            quantity=shipment_quantity,
            weight=weight,
            volume=volume,
            origin=origin,
            destination=destination,
            recepient_name=r_name,
            recepient_phone=r_phone,
            city=tocity,
            address=toaddress,
            status=status,
            shipment_cost=0.0
        )
        shipment.shipment_cost = shipment.calculate_rate
        shipment.save()

        return redirect('shipment_detail', shipment_id=shipment.id)

    return render(request, 'shipments/create_shipment.html', {'clients': clients})

# render shipment detail page
@login_required
def shipment_detail(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    client = get_object_or_404(Client, id=shipment.client_id)


    # Ensure only the client who created the shipment or an admin/staff can v---iew it
    if request.user != shipment.client and request.user.role not in ['admin', 'staff']:
        return render(request, '403.html', {'error': 'You are not authorized to view this shipment'})

    return render(request, 'shipments/shipment_detail.html', {'shipment': shipment, 'client': client})

# update shipment
@login_required
def update_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)

    if request.method == 'POST':
        shipment.weight = request.POST.get('weight', shipment.weight)
        shipment.volume = request.POST.get('volume', shipment.volume)
        shipment.destination = request.POST.get('destination', shipment.destination)
        shipment.status = request.POST.get('status', shipment.status)
        shipment.origin = request.POST.get('origin', shipment.origin)
        shipment.save()
        # Attempt to get the referring URL; IF NOT available fallback to the shipment list view
        referrer = request.META.get('HTTP_REFERER')
        if referrer: 
            return redirect(referrer)
        else:
            return redirect(reverse('getall_shipment'))
        

    return render(request, 'shipments/update_shipment.html', {'shipment': shipment})

# delete shipment
@login_required
def delete_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    shipment.delete()
    return redirect('getall_shipment')

# logic to track the shipment status
@login_required
def shipment_tracker(request):
    tracking_number = request.GET.get('tracking_number')
    shipment = None
    client = None

    if tracking_number:
        shipment = Shipment.objects.filter(tracking_number=tracking_number).first()
        if shipment and shipment.client_id:
            client = Client.objects.filter(id=shipment.client_id).first()

    return render(request, 'dash/shipment_tracker.html', {'shipment': shipment, 'client': client, 'tracking_number': tracking_number})

# logic to track the shipment status
@login_required
def track_shipment(request):
    tracking_number = request.GET.get('tracking_number')
    shipment = None
    client = None

    if tracking_number:
        shipment = Shipment.objects.filter(tracking_number=tracking_number).first()
        if shipment and shipment.client_id:
            client = Client.objects.filter(id=shipment.client_id).first()

    return render(request, 'shipments/track_shipment.html', {'shipment': shipment, 'client': client, 'tracking_number': tracking_number})

# generate the shipment invoice
@login_required
def generate_invoice(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    
    # Ensure an invoice does not already exist
    if Invoice.objects.filter(shipment=shipment).exists():
        return redirect('invoice_detail', shipment.invoice.id)

    # Generate a unique invoice number
    invoice_number = f"INV-{get_random_string(8).upper()}"  

    invoice = Invoice.objects.create(
        shipment=shipment,
        client=shipment.client,
        total_amount=shipment.calculate_rate,  # Assuming rate is the cost
        invoice_number=invoice_number  # Assigning the unique number
    )

    return redirect('invoice_detail', invoice.id)

# not currently in use
#def invoice_detail(request, invoice_id):
#    invoice = get_object_or_404(Invoice, id=invoice_id)
#    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

#@login_required
#def generate_invoice_pdfx(request, invoice_id):
    # Fetch the existing invoice
#    invoice = get_object_or_404(Invoice, id=invoice_id)
#
    # Load the invoice template
#    template_path = 'invoices/invoice_pdf.html'
#    context = {'invoice': invoice}
#   template = get_template(template_path)
#   html = template.render(context)

    # Create a PDF response
#    response = HttpResponse(content_type='application/pdf')
#    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'

    # Generate the PDF
#    pisa_status = pisa.CreatePDF(html, dest=response)

#    if pisa_status.err:
#        return HttpResponse('Error generating PDF <pre>' + html + '</pre>')

#   return response

