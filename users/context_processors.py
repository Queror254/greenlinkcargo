# users/context_processors.py
def business_context(request):
    user = request.user
    business = None

    if user.is_authenticated:
        if user.role == 'admin':
            business = getattr(user, 'business', None)
        elif user.role == 'staff':
            branch = getattr(user, 'branch', None)
            if branch:
                business = getattr(branch, 'business', None)

    return {'business': business}
