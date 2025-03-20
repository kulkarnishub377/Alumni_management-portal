from django.db import migrations, models
import uuid

def convert_ids_to_uuids(apps, schema_editor):
    Alumni = apps.get_model('alumni', 'Alumni')
    for alumni in Alumni.objects.all():
        alumni.id = uuid.uuid4()
        alumni.save()

class Migration(migrations.Migration):

    dependencies = [
        ('alumni', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumni',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True),
        ),
        migrations.RunPython(convert_ids_to_uuids),
    ]
