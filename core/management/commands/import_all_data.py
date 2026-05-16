import csv
from datetime import datetime

from django.core.management.base import BaseCommand
from core.models import (
    Employee,
    HierarchyLevel,
    Territory,
    Customer,
    CustomerAssignment,
    FinanceApplication,
    Loan,
    Installment
)


def safe_int(v):
    if v in [None, "", "null"]:
        return None
    return int(float(v))


def safe_float(v):
    if v in [None, "", "null"]:
        return None
    return float(v)


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Command(BaseCommand):
    help = "Import full system data from multiple CSV files"

    def handle(self, *args, **kwargs):

        # ----------------------------
        # 1. HIERARCHY LEVELS
        # ----------------------------
        hierarchy_map = {}

        for row in read_csv("data/hierarchy_levels.csv"):
            obj, _ = HierarchyLevel.objects.update_or_create(
                id=safe_int(row.get("id")),
                defaults={
                    "level_name": row["level_name"],
                    "level_rank": safe_int(row["level_rank"])
                }
            )
            hierarchy_map[obj.id] = obj

        # ----------------------------
        # 2. TERRITORIES (2-pass for parent)
        # ----------------------------
        territory_map = {}

        rows = read_csv("data/territories.csv")

        for row in rows:
            obj, _ = Territory.objects.update_or_create(
                id=safe_int(row.get("territory_id")),
                defaults={
                    "name": row["territory_name"]
                }
            )
            territory_map[obj.id] = obj

        for row in rows:
            obj = territory_map[safe_int(row.get("territory_id"))]
            parent_id = safe_int(row.get("parent_territory_id"))

            if parent_id:
                obj.parent = territory_map.get(parent_id)
                obj.save()

        # ----------------------------
        # 3. EMPLOYEES
        # ----------------------------
        employee_map = {}

        for row in read_csv("data/employees.csv"):
            obj, _ = Employee.objects.update_or_create(
                employee_id=safe_int(row["employee_id"]),
                defaults={
                    "employee_code": row["employee_code"],
                    "full_name": row["full_name"],
                    "email": row["email"] or None,
                    "phone": row["phone"] or None,
                    "hire_date": row["hire_date"],
                    "hierarchy_level_id": safe_int(row["hierarchy_level_id"]),
                    "territory_id": safe_int(row["territory_id"]),
                    "employment_status": row["employment_status"].lower(),
                }
            )
            employee_map[obj.employee_id] = obj

        # assign managers
        for row in read_csv("data/employees.csv"):
            emp_id = safe_int(row["employee_id"])
            manager_id = safe_int(row.get("manager_id"))

            if manager_id:
                employee_map[emp_id].manager = employee_map.get(manager_id)
                employee_map[emp_id].save()

        # ----------------------------
        # 4. CUSTOMERS
        # ----------------------------
        customer_map = {}

        for row in read_csv("data/users.csv"):
            obj, _ = Customer.objects.update_or_create(
                user_id=safe_int(row["user_id"]),

                national_id=row["national_id"],
                defaults={
                    "full_name": row["full_name"],
                    "phone": row["phone"],
                    "credit_score": safe_int(row["credit_score"]),
                    "monthly_salary": safe_float(row["salary"]),
                }
            )
            customer_map[obj.user_id] = obj

        # ----------------------------
        # 5. CUSTOMER ASSIGNMENTS
        # ----------------------------
        for row in read_csv("data/employee_customer_assignment.csv"):
            CustomerAssignment.objects.create(
                employee=employee_map[safe_int(row["employee_id"])],
                customer=customer_map[safe_int(row["user_id"])],
                status=row["assignment_status"]
            )

        # ----------------------------
        # 6. FINANCE APPLICATIONS
        # ----------------------------
        finance_map = {}

        for row in read_csv("data/finance.csv"):
            obj = FinanceApplication.objects.create(
                finance_id=safe_int(row["finance_id"]),
                user_id=customer_map[safe_int(row["user_id"])],
                requested_amount=safe_float(row["requested_amount"]),
                approved_amount=safe_float(row.get("approved_amount")),
                status=row["finance_status"]
            )
            finance_map[obj.finance_id] = obj

        # ----------------------------
        # 7. LOANS
        # ----------------------------
        loan_map = {}

        for row in read_csv("data/loan.csv"):
            finance = finance_map[safe_int(row["finance_id"])]

            obj = Loan.objects.create(
                loan_id=safe_int(row["loan_id"]),
                finance_id=finance,
                disbursed_amount=safe_float(row["disbursed_amount"]),
                interest_rate=safe_float(row["interest_rate"]),
                loan_status=row["loan_status"],
                dpd_count=safe_int(row["dpd"] or 0)
            )
            loan_map[obj.loan_id] = obj

        # ----------------------------
        # 8. INSTALLMENTS
        # ----------------------------
        for row in read_csv("data/installments.csv"):
            Installment.objects.create(
                loan_id=loan_map[safe_int(row["loan_id"])],
                due_date=row["due_date"],
                total_amount=safe_float(row["total_amount"]),
                paid_amount=safe_float(row["paid_amount"]),
                status=row["installment_status"]
            )

        self.stdout.write(self.style.SUCCESS("All CSVs imported successfully"))
