import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from .models import Book


def generate_barcode(book):
    # Use Code 128 instead of EAN-13
    CODE128 = barcode.get_barcode_class('code128')
    code128 = CODE128(book.book_id, writer=ImageWriter())
    
    # Create an in-memory buffer to hold the barcode image
    buffer = BytesIO()
    code128.write(buffer)
    buffer.seek(0)
    
    return buffer
   


def create_custom_label(book):
    # Generate barcode image
    barcode_img = generate_barcode(book)
    barcode_img = Image.open(barcode_img)
    
    # Define label dimensions (breadth x length)
    label_width = 200  # Small width
    label_height = 400  # Longer height

    # Create a new image with a rectangular label shape (no borders)
    new_img = Image.new('RGB', (label_width, label_height), 'white')
    
    # Prepare drawing context
    draw = ImageDraw.Draw(new_img)
    try:
        # Using built-in fonts for simplicity; adjust paths if custom fonts are needed
        font_bold = ImageFont.truetype("arialbd.ttf", 18)  # Bold font
        font_normal = ImageFont.truetype("arial.ttf", 14)  # Regular font
    except IOError:
        font_bold = ImageFont.load_default()
        font_normal = ImageFont.load_default()

    # Calculate barcode position (centered)
    barcode_width, barcode_height = barcode_img.size
    barcode_x = (label_width - barcode_width) // 2
    barcode_y = (label_height - barcode_height) // 2

    # Paste the barcode image in the middle
    new_img.paste(barcode_img, (barcode_x, barcode_y))
    
    # Draw the stack name above the barcode
    stack_name_text = f"Stack: {book.stack_name}"
    stack_name_bbox = draw.textbbox((0, 0), stack_name_text, font=font_bold)
    stack_name_width = stack_name_bbox[2] - stack_name_bbox[0]
    stack_name_height = stack_name_bbox[3] - stack_name_bbox[1]
    draw.text(((label_width - stack_name_width) // 2, barcode_y - stack_name_height - 10), stack_name_text, font=font_bold, fill='black')
    
    # Draw the book ID below the barcode
    book_id_text = f"Book ID: {book.book_id}"
    book_id_bbox = draw.textbbox((0, 0), book_id_text, font=font_bold)
    book_id_width = book_id_bbox[2] - book_id_bbox[0]
    book_id_height = book_id_bbox[3] - book_id_bbox[1]
    draw.text(((label_width - book_id_width) // 2, barcode_y + barcode_height + 10), book_id_text, font=font_bold, fill='black')

    # Save to a BytesIO object
    output = BytesIO()
    new_img.save(output, format='PNG')
    output.seek(0)
    return output