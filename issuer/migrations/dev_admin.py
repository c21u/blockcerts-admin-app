from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import User


def forwards(apps, schema_editor):
    if not settings.DEBUG:
        return
    User.objects.create_user(
            username="casuser",
            is_staff=True,
            is_superuser=True,
            is_active=True
    )


class Migration(migrations.Migration):

    dependencies = [
            ("issuer", "0004_auto_20190805_1841")
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
