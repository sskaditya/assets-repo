"""
Utility functions for the asset management system
"""
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw


def generate_qr_code(data, asset_tag=None):
    """
    Generate a QR code image from the given data
    
    Args:
        data: String data to encode in QR code (typically a UUID or URL)
        asset_tag: Optional asset tag to include in the filename
    
    Returns:
        File object containing the QR code image
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    
    # Add data
    qr.add_data(str(data))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Create filename
    filename = f"qr_{asset_tag if asset_tag else data}.png"
    
    return File(buffer, name=filename)


def generate_qr_code_with_label(data, label_text, asset_tag=None):
    """
    Generate a QR code image with a label below it
    
    Args:
        data: String data to encode in QR code
        label_text: Text to display below the QR code
        asset_tag: Optional asset tag to include in the filename
    
    Returns:
        File object containing the QR code image with label
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    
    qr.add_data(str(data))
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to RGB
    if qr_img.mode != 'RGB':
        qr_img = qr_img.convert('RGB')
    
    # Create new image with extra space for label
    qr_width, qr_height = qr_img.size
    label_height = 60
    new_height = qr_height + label_height
    
    new_img = Image.new('RGB', (qr_width, new_height), 'white')
    new_img.paste(qr_img, (0, 0))
    
    # Add label text
    draw = ImageDraw.Draw(new_img)
    
    # Calculate text position (centered)
    text_bbox = draw.textbbox((0, 0), label_text)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (qr_width - text_width) // 2
    text_y = qr_height + 10
    
    draw.text((text_x, text_y), label_text, fill='black')
    
    # Save to BytesIO
    buffer = BytesIO()
    new_img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Create filename
    filename = f"qr_{asset_tag if asset_tag else data}.png"
    
    return File(buffer, name=filename)


def get_asset_qr_url(request, qr_code_uuid):
    """
    Generate the full URL for an asset based on its QR code UUID
    
    Args:
        request: Django request object
        qr_code_uuid: UUID of the asset's QR code
    
    Returns:
        Full URL string
    """
    from django.urls import reverse
    
    # Build the absolute URI
    path = reverse('assets:asset_detail_by_qr', kwargs={'qr_code': str(qr_code_uuid)})
    return request.build_absolute_uri(path)
