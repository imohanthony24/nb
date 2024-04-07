from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import *
from .models import *
from django.contrib import messages
# Create your views here.
def homepage2(request):
    return render(request, "basex7.html")#index_generic.html")

def about(request):
    return render(request, "about.html",{})

def services(request):
    return render(request, "services.html",{})

class Contact(View):
    model = Contact
    form_class = ContactUsForm
    
    def get(self, request):
        return render(request, "contactus.html",{})
    def post(self, request):
        bounded_form = self.form_class(request.POST)
        if bounded_form.is_valid():
            obj = bounded_form.save()
            messages.info(request, "Data saved successfully. We will reach you by mail")
            return redirect('homepage')
        else:
            messages.info(request, "There was an error processing your form. Please contact us by mail")
            return redirect('homepage')