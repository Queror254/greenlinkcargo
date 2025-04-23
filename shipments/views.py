from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Shipment, Invoice
from setting_app.models import Rates
from clients.models import Client
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa

@login_required
def getall_shipment(request):
    shipments = Shipment.objects.all()
     # Ensure only the client who created the shipment or an admin/staff can view it
    if not request.user.is_authenticated:
        return render(request, '403.html', {'error': 'You are not authorized to view this shipment'})
    return render(request, 'shipments/shipment_list.html', {'shipments': shipments})
    
@login_required
def createshipment_view(request):
    clients = Client.objects.all()
    
    if request.method == 'POST':
        client_id = request.POST.get('client')
        
        if client_id:
            client = get_object_or_404(Client, id=client_id)
        else:
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
        weight = request.POST.get('weight')
        volume = request.POST.get('volume')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
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
        if shipment_type == 'air':
            shipment_cost = weight * rate.weight_rate
        elif shipment_type == 'sea':
            shipment_cost = volume * rate.cbm_rate
        else:
            shipment_cost = 0.0  # Default case (should not happen)

        # Create the shipment
        shipment = Shipment.objects.create(
            client=client,
            shipment_type=shipment_type,
            airwaybill=Airwaybill,
            seawaybill=Seawaybill,
            weight=weight,
            volume=volume,
            origin=origin,
            destination=destination,
            city=tocity,
            address=toaddress,
            status=status,
            shipment_cost=shipment_cost  # Save calculated shipment cost
        )

        return redirect('shipment_detail', shipment_id=shipment.id)

    return render(request, 'shipments/create_shipment.html', {'clients': clients})



@login_required
def shipment_detail(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    client = get_object_or_404(Client, id=shipment.client_id)


    # Ensure only the client who created the shipment or an admin/staff can v---iew it
    if request.user != shipment.client and request.user.role not in ['admin', 'staff']:
        return render(request, '403.html', {'error': 'You are not authorized to view this shipment'})

    return render(request, 'shipments/shipment_detail.html', {'shipment': shipment, 'client': client})

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

@login_required
def delete_shipment(request, shipment_id):
    shipment = get_object_or_404(Shipment, id=shipment_id)
    shipment.delete()
    return redirect('getall_shipment')

def shipment_tracker(request):
    tracking_number = request.GET.get('tracking_number')
    shipment = None
    client = None

    if tracking_number:
        shipment = Shipment.objects.filter(tracking_number=tracking_number).first()
        if shipment and shipment.client_id:
            client = Client.objects.filter(id=shipment.client_id).first()

    return render(request, 'dash/shipment_tracker.html', {'shipment': shipment, 'client': client, 'tracking_number': tracking_number})


def track_shipment(request):
    tracking_number = request.GET.get('tracking_number')
    shipment = None
    client = None

    if tracking_number:
        shipment = Shipment.objects.filter(tracking_number=tracking_number).first()
        if shipment and shipment.client_id:
            client = Client.objects.filter(id=shipment.client_id).first()

    return render(request, 'shipments/track_shipment.html', {'shipment': shipment, 'client': client, 'tracking_number': tracking_number})

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

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

def generate_invoice_pdf(request, invoice_id):
    # Fetch the existing invoice
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Load the invoice template
    template_path = 'invoices/invoice_pdf.html'
    context = {'invoice': invoice}
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF <pre>' + html + '</pre>')

    return response

