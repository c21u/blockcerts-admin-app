import csv
import os
import sqlite3
# sys.path.insert(0, "/Users/divyegala/PycharmProjects/admin_app") # /home/projects/my-djproj
#
# from manage import DEFAULT_SETTINGS_MODULE
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)

import django


def populate_persons():
    with open('person.csv') as f:
        reader = csv.reader(f)
        seen_emails = set()
        seen_public_addresses = set()
        for row in reader:
            try:
                if row[3] not in seen_emails and row[4] not in seen_public_addresses:
                    _, created = Person.objects.get_or_create(
                        first_name=row[1],
                        last_name=row[2],
                        email=row[3],
                        public_address=row[4]
                    )
                    seen_emails.add(row[3])
                    if row[4] != '':
                        seen_public_addresses.add(row[4])
            except sqlite3.IntegrityError as s:
                pass


if __name__ == '__main__':
    print("Starting persons population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_app.settings')
    django.setup()
    from issuer.models import Person
    populate_persons()