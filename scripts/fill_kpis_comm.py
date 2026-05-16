import csv
from datetime import datetime
from django.utils.dateparse import parse_date
from core.models import Employee, Loan, EmployeeKPI, Commission

# File Paths (Adjust these to match your actual folders)
KPI_CSV_PATH = "data/employee_kpi.csv"
COMMISSION_CSV_PATH = "data/commissions.csv"


def run():
    print("--- Starting Data Import ---")
    import_kpis()
    import_commissions()
    print("--- Data Import Complete ---")


def import_kpis():
    print(f"Reading KPIs from {KPI_CSV_PATH}...")
    kpis_to_create = []

    with open(KPI_CSV_PATH, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            kpi_id = int(row["kpi_id"])
            emp_id = int(row["employee_id"])

            # Prevent duplicate primary keys if script is re-run
            if EmployeeKPI.objects.filter(kpi_id=kpi_id).exists():
                continue

            try:
                employee_instance = Employee.objects.get(pk=emp_id)
            except Employee.DoesNotExist:
                print(f"Skipping KPI {kpi_id}: Employee {emp_id} not found.")
                continue

            # Parse date string (expects YYYY-MM-DD format like '2026-05-15')
            date_str = row["month"].strip()
            calc_month = parse_date(date_str)
            if not calc_month:
                # Fallback if date is written as YYYY-MM
                try:
                    calc_month = datetime.strptime(date_str, "%Y-%m").date()
                except ValueError:
                    print(
                        f"Skipping KPI {kpi_id}: Invalid date format '{date_str}'.")
                    continue

            kpis_to_create.append(
                EmployeeKPI(
                    kpi_id=kpi_id,
                    employee_id=employee_instance,  # Assign instance to ForeignKey field
                    target_amount=float(row["target_amount"]),
                    achieved_amount=float(row["achieved_amount"]),
                    calculation_month=calc_month,
                )
            )

    # Insert everything at once safely
    if kpis_to_create:
        EmployeeKPI.objects.bulk_create(kpis_to_create)
        print(f"Successfully imported {len(kpis_to_create)} KPI records.")


def import_commissions():
    print(f"Reading Commissions from {COMMISSION_CSV_PATH}...")
    commissions_to_create = []

    with open(COMMISSION_CSV_PATH, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            comm_id = int(row["commission_id"])
            emp_id = int(row["employee_id"])
            loan_id = int(row["loan_id"])

            if Commission.objects.filter(commission_id=comm_id).exists():
                continue

            try:
                employee_instance = Employee.objects.get(pk=emp_id)
                loan_instance = Loan.objects.get(pk=loan_id)
            except Employee.DoesNotExist:
                print(f"Skipping Comm {comm_id}: Employee {emp_id} not found.")
                continue
            except Loan.DoesNotExist:
                print(f"Skipping Comm {comm_id}: Loan {loan_id} not found.")
                continue

            commissions_to_create.append(
                Commission(
                    commission_id=comm_id,
                    employee_id=employee_instance,
                    loan_id=loan_instance,
                    amount=float(row["commission_amount"]),
                )
            )

    if commissions_to_create:
        Commission.objects.bulk_create(commissions_to_create)
        print(
            f"Successfully imported {len(commissions_to_create)} Commission records.")
