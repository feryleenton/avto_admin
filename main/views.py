from django.shortcuts import render


def not_found(request):
    return render(request, 'main/404.html')
