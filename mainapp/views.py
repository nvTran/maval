from django.shortcuts import render

# Create your views here.
def landingpage(request):
    return render(request, "homepage.html")

def homepage(request):
    return render(request, "homepage.html")

