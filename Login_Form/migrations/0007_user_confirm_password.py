# Generated by Django 4.1.7 on 2024-03-26 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Login_Form', '0006_remove_user_confirm_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirm_password',
            field=models.TextField(null=True),
        ),
    ]
