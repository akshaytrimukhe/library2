# Generated by Django 5.0.7 on 2024-07-26 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_book_book_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='barcode_image',
            field=models.ImageField(blank=True, null=True, upload_to='barcodes/'),
        ),
    ]
