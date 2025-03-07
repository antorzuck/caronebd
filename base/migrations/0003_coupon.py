# Generated by Django 5.1.3 on 2025-02-11 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_product_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
