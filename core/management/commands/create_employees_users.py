from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Employee


class Command(BaseCommand):
    help = "Create and link users for employees"

    def handle(self, *args, **kwargs):
        for emp in Employee.objects.all():

            user, created = User.objects.get_or_create(
                username=emp.employee_code
            )

            # ALWAYS update fields
            if emp.full_name:
                parts = emp.full_name.strip().split()
                user.first_name = parts[0]
                user.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

            user.email = emp.email
            user.is_active = True

            if created:
                user.set_password("Temp1234!")

            user.save()

            emp.user = user
            emp.save()

        self.stdout.write(self.style.SUCCESS(
            "Users created and linked successfully"))
