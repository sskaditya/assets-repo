import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Asset, AssetHistory

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Asset)
def generate_asset_qr_code(sender, instance, created, **kwargs):
    """
    Generate QR code for asset after it's created
    """
    if created and not instance.qr_code_image:
        try:
            from core.utils import generate_qr_code_with_label
            from django.conf import settings
            
            domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
            protocol = 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'
            asset_url = f"{protocol}://{domain}/app/assets/qr/{instance.qr_code}/"
            
            qr_file = generate_qr_code_with_label(
                data=asset_url,
                label_text=instance.asset_tag,
                asset_tag=instance.asset_tag
            )
            instance.qr_code_image.save(qr_file.name, qr_file, save=True)
        except Exception as e:
            logger.error(f"Failed to generate QR code for asset {instance.asset_tag}: {e}")


@receiver(post_save, sender=Asset)
def create_asset_history(sender, instance, created, **kwargs):
    """
    Create history entry when asset is created
    """
    if created:
        try:
            AssetHistory.objects.create(
                asset=instance,
                action_type='CREATED',
                remarks=f'Asset {instance.asset_tag} created'
            )
        except Exception as e:
            logger.error(f"Failed to create history for asset {instance.asset_tag}: {e}")
