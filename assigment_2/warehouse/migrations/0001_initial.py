# Generated by Django 4.2.20 on 2025-03-21 01:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('unit', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('stock', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('balance', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseHeader',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-date', 'code'],
            },
        ),
        migrations.CreateModel(
            name='SellHeader',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-date', 'code'],
            },
        ),
        migrations.CreateModel(
            name='SellDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=15)),
                ('header', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='details', to='warehouse.sellheader')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sell_details', to='warehouse.item')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PurchaseDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=15)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('remaining_quantity', models.DecimalField(decimal_places=2, max_digits=15)),
                ('header', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='details', to='warehouse.purchaseheader')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchase_details', to='warehouse.item')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
