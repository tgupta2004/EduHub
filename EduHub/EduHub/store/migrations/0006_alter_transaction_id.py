# Generated by Django 5.1.1 on 2024-09-25 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_transaction_amount_transaction_confirmed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
