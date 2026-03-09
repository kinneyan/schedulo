from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0009_alter_shift_member"),
    ]

    operations = [
        migrations.RenameField(
            model_name="memberpermissions",
            old_name="IS_OWNER",
            new_name="is_owner",
        ),
        migrations.RenameField(
            model_name="memberpermissions",
            old_name="MANAGE_WORKSPACE_MEMBERS",
            new_name="manage_workspace_members",
        ),
        migrations.RenameField(
            model_name="memberpermissions",
            old_name="MANAGE_WORKSPACE_ROLES",
            new_name="manage_workspace_roles",
        ),
        migrations.RenameField(
            model_name="memberpermissions",
            old_name="MANAGE_SCHEDULES",
            new_name="manage_schedules",
        ),
        migrations.RenameField(
            model_name="memberpermissions",
            old_name="MANAGE_TIME_OFF",
            new_name="manage_time_off",
        ),
    ]
