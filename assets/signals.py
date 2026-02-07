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
        
        # Generate QR code with asset tag as label
        qr_file = generate_qr_code_with_label(
            data=str(instance.qr_code),
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
