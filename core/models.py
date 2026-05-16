from datetime import date

from django.db import models
from django.contrib.auth.models import User

# =========================
# 1. ORGANIZATION
# =========================


class HierarchyLevel(models.Model):
    level_name = models.CharField(max_length=50)
    level_rank = models.IntegerField()

    def __str__(self):
        return self.level_name


class Territory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Employee(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)

    employee_id = models.IntegerField(
        primary_key=True)

    employee_code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    hire_date = models.DateField()

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates"
    )

    hierarchy_level_id = models.ForeignKey(
        HierarchyLevel, on_delete=models.SET_NULL, null=True)
    territory_id = models.ForeignKey(
        Territory, on_delete=models.SET_NULL, null=True)

    employment_status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("resigned", "Resigned"),
        ],
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    @property
    def name_initials(self):
        initials = " ".join([word[0].upper()
                            for word in self.full_name.split(maxsplit=1)])
        return initials

# =========================
# 2. CRM (Customers)
# =========================


class Customer(models.Model):
    CUSTOMER_STATUS = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Rejected', 'Rejected'),
    ]
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=20, null=True)

    credit_score = models.IntegerField()
    monthly_salary = models.FloatField()
    status = models.CharField(
        max_length=20, choices=CUSTOMER_STATUS, default='Pending')

    def __str__(self):
        return self.full_name

    @property
    def name_initials(self):
        initials = " ".join([word[0].upper()
                            for word in self.full_name.split(maxsplit=1)])
        return initials


class CustomerAssignment(models.Model):

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Transferred', 'Transferred'),
        ('Terminated', 'Terminated'),
    ]
    assignment_id = models.AutoField(primary_key=True)

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    assigned_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.customer} → {self.employee}"


# =========================
# 3. FINANCE CORE
# =========================

class FinanceApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    finance_id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey(Customer, on_delete=models.CASCADE)

    requested_amount = models.FloatField()
    approved_amount = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Finance {self.finance_id} - {self.status}"


class Loan(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
        ('Delayed', 'Delayed'),
    ]

    loan_id = models.IntegerField(primary_key=True)

    finance_id = models.OneToOneField(
        FinanceApplication, on_delete=models.CASCADE)

    disbursed_amount = models.FloatField()
    interest_rate = models.FloatField()
    installment_amount = models.FloatField()
    tenure = models.IntegerField()
    outstanding_balance = models.FloatField()

    loan_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    dpd_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Loan {self.loan_id}"


class Installment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
        ('Overdue', 'Overdue'),
    ]

    installment_id = models.IntegerField(primary_key=True)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE)

    due_date = models.DateField()
    total_amount = models.FloatField()
    paid_amount = models.FloatField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Installment {self.installment_id}"

    @property
    def dpd(self):
        if self.status == 'Paid':
            return 0

        today = date.today()
        if today <= self.due_date:
            return 0

        delta = today - self.due_date
        return delta.days


class EmployeeKPI(models.Model):
    kpi_id = models.IntegerField(primary_key=True)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    target_amount = models.FloatField()
    achieved_amount = models.FloatField()
    calculation_month = models.DateField()
    collection_rate = models.FloatField()

    def __str__(self):
        return f"Empoyee KPI {self.kpi_id}"

    @property
    def achievement_rate(self):
        if not self.target_amount:
            return 0
        return round(self.achieved_amount / self.target_amount * 100, 2)

    @property
    def achieved_amount_formatted(self):
        if not self.achieved_amount:
            return 0
        return f"{int(self.achieved_amount):,}"

    @property
    def target_amount_formatted(self):
        if not self.target_amount:
            return 0
        return f"{int(self.target_amount):,}"


class Commission(models.Model):
    commission_id = models.IntegerField(primary_key=True)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return f"Commission Amount: {self.amount}"
