# Generated by Django 5.1.3 on 2024-12-26 18:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_workspacerole_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shift',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.workspacemember'),
        ),
    ]