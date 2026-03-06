from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [("spare", "0001_initial")]
    operations = [migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS pg_trgm;")]