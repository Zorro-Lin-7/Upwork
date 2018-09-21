from django.shortcuts import render


def home(request):
    """
    Render home template
    """
    return render(request, 'home.html')

