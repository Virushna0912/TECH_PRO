# Generated by Django 5.1 on 2024-08-15 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_orderplaced_status_wishlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderplaced',
            name='status',
            field=models.CharField(choices=[('On The Way', 'On The Way'), ('Delivered', 'Delivered'), ('Cancel', 'Cancel'), ('Pending', 'Pending'), ('Packed', 'Packed'), ('Accepted', 'Accepted')], default='pending', max_length=50),
        ),
    ]
