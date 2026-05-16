import csv
from datetime import datetime

from django.core.management.base import BaseCommand
from core.models import Employee


class Command(BaseCommand):
    help = "Import employees from CSV"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs["csv_file"]

        # first pass: create employees without managers
        with open(file_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            employees_cache = {}

            for row in reader:
                employee_id = safe_int(row["employee_id"])

                employee, created = Employee.objects.update_or_create(
                    employee_id=employee_id,
                    defaults={
                        "employee_code": row["employee_code"],
                        "full_name": row["full_name"],
                        "email": row["email"] or None,
                        "phone": row["phone"] or None,
                        "hire_date": datetime.strptime(row["hire_date"], "%Y-%m-%d").date(),
                        "hierarchy_level_id": int(row["hierarchy_level_id"]),
                        "territory_id": int(row["territory_id"]),
                        "employment_status": row["employment_status"].lower(),
                    },
                )

                employees_cache[employee_id] = {
                    "obj": employee,
                    "manager_id": row.get("manager_id") or None
                }

        # second pass: assign managers (because self FK needs existing rows)
        for emp_id, data in employees_cache.items():
            manager_id = data["manager_id"]

            if manager_id:
                try:
                    data["obj"].manager = Employee.objects.get(
                        employee_id=safe_int(manager_id))
                    data["obj"].save()
                except Employee.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Manager not found for employee {emp_id}")
                    )

        self.stdout.write(self.style.SUCCESS("Import completed successfully"))


def safe_int(value):
    if value is None or value == "":
        return None
    return int(float(value))
