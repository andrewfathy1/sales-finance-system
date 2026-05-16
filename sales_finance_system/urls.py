"""
URL configuration for sales_finance_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from employee_login import views as login_views
# from employee_dashboard import views as dashboard_views
from django.contrib.auth.views import LogoutView
from main_dashboard import views as main_dashboard_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('login/', login_views.employee_login, name='employee-login'),
    # path('dashboard/', dashboard_views.dashboard_home, name='dashboard-home'),
    # path('dashboard/customers', dashboard_views.dashboard_customers,
    #      name='dashboard-customers'),
    path('logout/', LogoutView.as_view(next_page='employee-login'), name='logout'),

    path('dashboard/', main_dashboard_views.dashboard_main, name='main-dashboard'),

]
