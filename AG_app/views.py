from django.shortcuts import render, redirect
from .models import Teachers, ExamEvents, ExamVenues, Contacts
from .forms import ContactForm


# Create your views here.

#Teachers details
def teacher_list(request):
    teachers = Teachers.objects.all()
    return render(request, 'teachers/list.html', {'teachers': teachers})

#Contact
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_thanks')
    else:
        form = ContactForm()
    return render(request, 'contact/form.html', {'form': form})
