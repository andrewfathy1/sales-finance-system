from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from core.models import Employee, Territory, CustomerAssignment


@login_required
def dashboard_home(request):
    employee = Employee.objects.get(user=request.user)

    reporting_chain = []

    current = employee.manager

    while current:
        reporting_chain.append(current.full_name)
        current = current.manager

    reporting_chain.reverse()
    reporting_chain.append("You")

    territory_chain = []
    current_territory = employee.territory_id
    while current_territory:
        territory_chain.append(current_territory.name)
        current_territory = current_territory.parent

    # Customers (example relation)
    # customers = Customer.objects.filter(territory__in=territories)

    context = {
        "employee": employee,
        "reporting_chain": reporting_chain,
        'territory_chain': territory_chain,
        # "customers": customers,
    }

    return render(request, 'employee_dashboard/dashboard.html', context)


@login_required
def dashboard_customers(request):
    employee = Employee.objects.get(user=request.user)

    assignments = CustomerAssignment.objects.filter(
        employee=employee.employee_id,
    ).select_related("customer")

    customers = [a.customer for a in assignments]

    customer_count = len(customers)

    return render(request, 'employee_dashboard/customer_dashboard.html', {
        'customers': customers,
        'customer_count': customer_count
    })
