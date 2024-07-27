from django.db import models

# Create your models here.

class Book(models.Model):
    book_id = models.CharField(max_length=100)
    stack_name = models.CharField(max_length=100)
    library_name = models.CharField(max_length=100)
    barcode_image = models.ImageField(upload_to='barcodes/', null=True, blank=True)

    def __str__(self):
        return self.book_id