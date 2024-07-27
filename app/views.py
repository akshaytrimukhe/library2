from venv import logger
import pandas as pd
from django.shortcuts import render,redirect
from .models import Book
from .forms import UploadFileForm
from django.http import HttpResponse
from .utils import create_custom_label
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Max
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import csv
import os
from django.conf import settings
import logging
import zipfile
# Create your views here.
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            for _, row in df.iterrows():
                book_id = row['book_id']
                # Check if the book_id already exists
                if not Book.objects.filter(book_id=book_id).exists():
                    # Assuming the barcode image is named after the book_id
                    barcode_image = f'barcodes/{book_id}.png'
                    Book.objects.create(
                        book_id=book_id,
                        stack_name=row['stack_name'],
                        library_name=row['library_name'],
                        barcode_image=barcode_image
                    )
                save_all_barcodes()
            return redirect('view_barcodes')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def display_barcode(request, book_id):
    try:
        # Try to get a single Book object
        book = Book.objects.filter(book_id=book_id).first()
        
        if not book:
            return HttpResponse("Book not found", status=404)
        
    except MultipleObjectsReturned:
        # Handle the case where multiple Book objects are returned
        book = Book.objects.filter(book_id=book_id).first()  # Choose the first one
        
    # Generate barcode image
    barcode_img = create_custom_label(book)

    return HttpResponse(barcode_img, content_type='image/png')



def book_list(request):
    # Group by book_id and get the first entry for each group
    books = Book.objects.values('book_id').annotate(
        max_id=Max('id')
    ).values('book_id', 'max_id')

    # Fetch the full Book objects for the selected ids
    book_ids = [book['max_id'] for book in books]
    unique_books = Book.objects.filter(id__in=book_ids)
    
    return render(request, 'book_list.html', {'books': unique_books})




def download_all_barcodes(request):
    # Directory where barcodes are stored
    barcode_dir = os.path.join(settings.MEDIA_ROOT, 'barcodes')
    logger.debug(f'Barcode directory: {barcode_dir}')
    
    # Check if the directory exists
    if not os.path.exists(barcode_dir):
        logger.error(f'Barcode directory does not exist: {barcode_dir}')
        return HttpResponse("Barcode directory does not exist.", status=404)

    file_list = os.listdir(barcode_dir)
    if not file_list:
        logger.error('No barcodes found in directory.')
        return HttpResponse("No barcodes found.", status=404)

    # Creating a zip file to download
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        for file_name in file_list:
            file_path = os.path.join(barcode_dir, file_name)
            zf.write(file_path, file_name)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="barcodes.zip"'
    return response


def save_all_barcodes():
    # Define the directory where barcodes will be saved
    barcode_dir = os.path.join(settings.MEDIA_ROOT, 'barcodes')
    if not os.path.exists(barcode_dir):
        os.makedirs(barcode_dir)

    # Retrieve all Book objects
    books = Book.objects.all()

    for book in books:
        # Define the file path for the barcode image
        file_path = os.path.join(barcode_dir, f'{book.book_id}.png')

        # Skip if the file already exists
        if os.path.exists(file_path):
            continue

        barcode_img = create_custom_label(book)

        # Save the barcode image to a file
        with open(file_path, 'wb') as f:
            f.write(barcode_img.read())

    return HttpResponse("All files saved")



def view_barcodes(request):
    books = Book.objects.all()
    context = {
        'books': books
    }
    return render(request, 'view_barcodes.html', context)