from django.utils import timezone, dateformat


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Employee, Customer, CustomerAssignment, FinanceApplication, Loan, EmployeeKPI, Commission, Installment


@login_required
def dashboard_main(request):

    # -------------------------------------------- Employee Details -------------------------------------------------#

    employee = Employee.objects.get(user=request.user)

    reporting_chain = []

    current = employee.manager

    while current:
        reporting_chain.append(current)
        current = current.manager

    reporting_chain.reverse()
    # reporting_chain.append("You")

    territory_chain = []
    current_territory = employee.territory_id
    while current_territory:
        territory_chain.append(current_territory.name)
        current_territory = current_territory.parent
    # -------------------------------------------- Customers -------------------------------------------------#

    assignments = CustomerAssignment.objects.filter(
        employee=employee.employee_id,
    ).select_related("customer")

    customers_json = [
        {
            "id": a.customer.user_id,
            "name": a.customer.full_name,
            "city": a.customer.city,
            "national_id": a.customer.national_id,
            "phone": a.customer.phone,
            "credit_score": a.customer.credit_score,
            "salary": a.customer.monthly_salary,
            "status": a.customer.status.lower(),
            "initials": a.customer.name_initials,
        }
        for a in assignments]

    customers = [a.customer for a in assignments]
    customer_count = len(customers)

    active_customers = [a for a in customers if a.status == "Active"]
    active_customers_count = len(active_customers)

    employee_pending_customers = [
        a for a in customers if a.status == "Pending"]
    employee_pending_customers_count = len(employee_pending_customers)

    employee_rejected_customers = [
        a for a in customers if a.status == "Rejected"]
    employee_rejected_customers_count = len(employee_rejected_customers)

    pending_customers = Customer.objects.filter(status='Pending')
    pending_customer_count = len(pending_customers)

    customers_chart_data = {
        'total': customer_count,
        'active': active_customers_count,
        'pending': employee_pending_customers_count,
        'rejected': employee_rejected_customers_count
    }

    # -------------------------------------------- Loans -------------------------------------------------#
    user_ids = [c.user_id for c in customers]

    all_loans = Loan.objects.filter(
        finance_id__user_id__in=user_ids
    )

    delayed_loans = [
        loan for loan in all_loans if loan.loan_status == 'Delayed']

    # -------------------------------------------- Installments -------------------------------------------------#
    loan_ids = [l.loan_id for l in all_loans]

    employee_installments = Installment.objects.filter(loan_id__in=loan_ids)

    upcoming_installments = [
        {
            "id": inst.installment_id,
            "amount": float(inst.total_amount),
            "due_date": inst.due_date.strftime("%Y-%m-%d"),
            "status": inst.status,
            "dpd": inst.dpd,
        }
        for inst in employee_installments
        if inst.status in ["Pending", "Overdue", "Partial"]
    ][:10]

    # -------------------------------------------- KPIs -------------------------------------------------#

    kpi_record = EmployeeKPI.objects.filter(
        employee_id=employee.employee_id).first()

    employee_kpi_chart_data = {
        'achieved': int(kpi_record.achieved_amount or 0) if kpi_record else 0,
        'target': int(kpi_record.target_amount or 0) if kpi_record else 0,
    }

    # -------------------------------------------- Commis sions -------------------------------------------------#

    commissions = Commission.objects.filter(employee_id=employee.employee_id)
    total_earned = sum([comm.amount for comm in commissions])
    total_earned = f"{int(total_earned):,}"
    # commission_table = [
    #     {
    #         "loan_id": comm.loan_id,
    #         'disbursed': [loan for loan in all_loans if loan.id == comm.loan_id][0].disbursed_amount,
    #         "customer": float(comm.total_amount),
    #         "due_date": comm.due_date.strftime("%Y-%m-%d"),
    #         "status": comm.status,
    #         "dpd": comm.dpd,
    #     }
    #     for comm in commissions
    #     if comm.status in ["Pending", "Overdue", "Partial"]
    # ]

    # -------------------------------------------- Date -------------------------------------------------#

    current_date = timezone.now()
    # formatted_date = dateformat.format(current_date, 'l, d F Y H:i')
    formatted_date = current_date.strftime("%A, %d %B %Y")

    # -------------------------------------------- Final data -------------------------------------------------#

    context = {

        'date': formatted_date,
        "employee": employee,

        "reporting_chain": reporting_chain,
        'territory_chain': territory_chain,


        "customers": customers_json,
        'customer_count': customer_count,
        "pending_customers": pending_customers,
        'pending_customer_count': pending_customer_count,
        "active_customers": active_customers,
        "active_customers_count": active_customers_count,
        'employee_pending_customers_count': employee_pending_customers_count,
        'employee_rejected_customers_count': employee_rejected_customers_count,
        'employee_active_customers_rate': round(active_customers_count/customer_count * 100, 2) if customer_count else 0,
        'employee_customer_chart_data': customers_chart_data,
        'employee_kpi_chart_data': employee_kpi_chart_data,
        # 'all_loans': all_loans,
        # 'delayed_loans': delayed_loans,
        'delayed_loans_count': len(delayed_loans),



        # 'all_installments': employee_installments,
        'upcoming_installments': upcoming_installments,

        'kpi_record': kpi_record,

        'commissions': commissions,
        'total_earned': total_earned,
        'total_commissions': commissions.__len__,

    }

    return render(request, 'main_dashboard/main_dashboard.html', context)
