# myapp/migrations/0002_auto_20241106_2225.py
from django.db import migrations, models
from django.utils import timezone

def set_default_last_hit_time(apps, schema_editor):
    CustomUser = apps.get_model('myapp', 'CustomUser')
    for user in CustomUser.objects.all():
        if not user.last_hit_time:
            user.last_hit_time = timezone.now()  
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),  
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_hit_time',
            field=models.DateTimeField(default=timezone.now),
        ),
        migrations.RunPython(set_default_last_hit_time)
    ]
