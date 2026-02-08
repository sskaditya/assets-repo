from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Asset, AssetHistory


@receiver(post_save, sender=Asset)
def generate_asset_qr_code(sender, instance, created, **kwargs):
    """
    Generate QR code for asset after it's created
    """
    if created and not instance.qr_code_image:
        from core.utils import generate_qr_code_with_label
        from django.conf import settings
        
        # Construct the full URL for the asset
        # Use the domain from settings or a default
        domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
        protocol = 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'
        
        # Build the asset URL with QR code
        asset_url = f"{protocol}://{domain}/app/assets/qr/{instance.qr_code}/"
        
        # Generate QR code with the full URL and asset tag as label
        qr_file = generate_qr_code_with_label(
            data=asset_url,
            label_text=instance.asset_tag,
            asset_tag=instance.asset_tag
        )
        
        # Save the QR code image
        instance.qr_code_image.save(qr_file.name, qr_file, save=True)


@receiver(post_save, sender=Asset)
def create_asset_history(sender, instance, created, **kwargs):
    """
    Create history entry when asset is created or updated
    """
    if created:
        AssetHistory.objects.create(
            asset=instance,
            action_type='CREATED',
            remarks=f'Asset {instance.asset_tag} created'
        )
