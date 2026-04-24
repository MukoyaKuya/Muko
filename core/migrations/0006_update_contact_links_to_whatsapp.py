from django.db import migrations, models


WHATSAPP_URL = 'https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.'


def update_contact_links(apps, schema_editor):
	ShopItem = apps.get_model('core', 'ShopItem')
	ShopSectionSettings = apps.get_model('core', 'ShopSectionSettings')

	ShopItem.objects.filter(link_url='#contact').update(link_url=WHATSAPP_URL)
	ShopSectionSettings.objects.filter(primary_cta_url='#contact').update(primary_cta_url=WHATSAPP_URL)


class Migration(migrations.Migration):

	dependencies = [
		('core', '0005_shopitem_fields_and_sectionsettings'),
	]

	operations = [
		migrations.AlterField(
			model_name='shopitem',
			name='link_url',
			field=models.CharField(blank=True, help_text='Optional destination URL for the card CTA.', max_length=255),
		),
		migrations.AlterField(
			model_name='shopsectionsettings',
			name='primary_cta_url',
			field=models.CharField(default=WHATSAPP_URL, max_length=255),
		),
		migrations.RunPython(update_contact_links, migrations.RunPython.noop),
	]