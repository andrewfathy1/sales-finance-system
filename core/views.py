from django.shortcuts import render, redirect


# Create your views here.
def home(request):
    # return render(request, 'employee_login/login.html')
    return redirect('employee-login')
