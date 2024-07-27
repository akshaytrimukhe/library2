from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('barcode/<str:book_id>/', views.display_barcode, name='display_barcode'),
    path('books/', views.book_list, name='book_list'),
    path('download-barcodes/', views.download_all_barcodes, name='download_all_barcodes'),
    path('view-barcodes/', views.view_barcodes, name='view_barcodes'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

