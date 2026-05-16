import csv
from core.models import Customer as User

CSV_FILE_PATH = "data/users.csv"

# Allowed choices from your Customer model definition
VALID_STATUSES = {"Pending", "Active", "Rejected"}


def run():
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            user_id = safe_int(row["user_id"])
            status = row["customer_status"].strip() if row.get(
                "customer_status") else None

            # Validate that the CSV status matches your model choices
            if status not in VALID_STATUSES:
                print(f"Skipping user {user_id}: Invalid status '{status}'")
                continue

            try:
                user = User.objects.get(user_id=user_id)
                user.status = status
                user.save(update_fields=["status"])  # ONLY updates status

                print(f"Updated user {user_id} status → {status}")

            except User.DoesNotExist:
                print(f"User not found: {user_id}")


def safe_int(v):
    if v in [None, "", "null"]:
        return None
    return int(float(v))


if __name__ == "__main__":
    run()
