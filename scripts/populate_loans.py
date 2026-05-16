import csv
from core.models import Loan


def run():
    path = 'data/loan.csv'
    updated = 0
    skipped = 0

    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                loan = Loan.objects.get(loan_id=row['loan_id'])
                loan.tenure = float(row['tenure_months'])
                loan.save(update_fields=[
                          'tenure',])
                updated += 1
            except Loan.DoesNotExist:
                print(f"Loan {row['loan_id']} not found, skipping")
                skipped += 1

    print(f"Done — {updated} updated, {skipped} skipped")
