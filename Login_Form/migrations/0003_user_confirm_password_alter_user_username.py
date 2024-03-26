# Generated by Django 4.1.7 on 2024-03-26 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Login_Form', '0002_rename_description_user_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirm_password',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
