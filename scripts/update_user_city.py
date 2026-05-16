import csv
from core.models import Customer as User


CSV_FILE_PATH = "data/users.csv"


def run():
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            user_id = safe_int(row["user_id"])
            city = row["city"]

            try:
                user = User.objects.get(user_id=user_id)
                user.city = city
                user.save(update_fields=["city"])  # ONLY updates city

                print(f"Updated {user_id} → {city}")

            except User.DoesNotExist:
                print(f"User not found: {user_id}")


if __name__ == "__main__":
    run()


def safe_int(v):
    if v in [None, "", "null"]:
        return None
    return int(float(v))
