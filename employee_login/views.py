from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate


def employee_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('main-dashboard')
            # return redirect('main-dashboard-home')
        else:
            return render(request, 'employee_login/login.html', {
                'error': 'Invalid Employee ID or Password'
            })

    return render(request, 'employee_login/login.html')
