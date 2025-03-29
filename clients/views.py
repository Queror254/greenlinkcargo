from django.shortcuts import render, get_object_or_404, redirect
from .models import Client

def client_list(request):
    clients = Client.objects.all()  # Fetch all clients
    return render(request, 'clients/client_list.html', {'clients': clients})

def create_client(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postalcode = request.POST.get('postalcode')

        Client.objects.create(
            name=name, email=email, phone=phone,
            address=address, city=city, postalcode=postalcode
        )
        return redirect('client_list')  # Redirect after successful creation

    return render(request, 'clients/create_client.html')

def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/client_detail.html', {'client': client})

def update_client(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == 'POST':
        client.name = request.POST.get('name')
        client.email = request.POST.get('email')
        client.phone = request.POST.get('phone')
        client.address = request.POST.get('address')
        client.city = request.POST.get('city')
        client.postalcode = request.POST.get('postalcode')
        client.save()
        return redirect('client_list')  # Redirect to the client list after saving

    return render(request, 'clients/update_client.html', {'client': client})