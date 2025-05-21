from django.shortcuts import render, get_object_or_404, redirect
from .models import Client
from users.models import Business, Branch
from django.contrib.auth.decorators import login_required

@login_required
# render client list
def client_list(request):
    clients = Client.objects.all()  # Fetch all clients
    return render(request, 'clients/client_list.html', {'clients': clients})

@login_required
# create client logic
def create_client(request):
    #get the current logged in user
    user = request.user
    
    #initialize the branch variable
    branch=None
    #fetch the business based on the user role
    if user.role == 'admin':
        business = get_object_or_404(Business, owner=user)
    else:
        branch = user.branch 
        business = branch.business 
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postalcode = request.POST.get('postalcode')

        Client.objects.create(
            name=name, 
            email=email, 
            phone=phone,
            address=address, city=city, postalcode=postalcode, branch=branch, business=business
        )
        return redirect('client_list')  # Redirect after successful creation

    return render(request, 'clients/create_client.html') #render the client creation form

@login_required
#render client details
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/client_detail.html', {'client': client})

@login_required
#update client logic
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


@login_required
#delete client logic
def delete_client(request, pk):
    client = get_object_or_404(Client, id=pk)
    client.delete()
    return redirect('client_list')