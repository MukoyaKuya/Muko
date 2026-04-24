from django.db import migrations, models


def seed_shop_section_settings(apps, schema_editor):
	ShopItem = apps.get_model('core', 'ShopItem')
	ShopSectionSettings = apps.get_model('core', 'ShopSectionSettings')

	ShopItem.objects.filter(title='Website Templates').update(image_path='img/work3.png', link_url='#contact')
	ShopItem.objects.filter(title='Digital Assets').update(image_path='img/work1.png', link_url='#contact')
	ShopItem.objects.filter(title='Side-Hustle Apparel').update(image_path='img/bg.png', link_url='#contact')

	ShopSectionSettings.objects.get_or_create(
		id=1,
		defaults={
			'eyebrow': 'Shop',
			'heading': 'Digital Goods',
			'heading_highlight': '& Garments',
			'description': 'A curated storefront is coming soon for premium website templates, practical digital assets, and limited garment drops built around the same design language as the client work.',
			'primary_cta_label': 'Ask About The Shop',
			'primary_cta_url': '#contact',
			'secondary_badge_label': 'Launching Soon',
			'secondary_badge_icon': 'clock-3',
		},
	)


class Migration(migrations.Migration):

	dependencies = [
		('core', '0004_shopitem'),
	]

	operations = [
		migrations.AddField(
			model_name='shopitem',
			name='image_path',
			field=models.CharField(default='img/work3.png', help_text='Path relative to static/, for example img/work3.png', max_length=255),
			preserve_default=False,
		),
		migrations.AddField(
			model_name='shopitem',
			name='link_url',
			field=models.CharField(blank=True, help_text='Optional destination URL or anchor such as #contact.', max_length=255),
		),
		migrations.CreateModel(
			name='ShopSectionSettings',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('eyebrow', models.CharField(default='Shop', max_length=80)),
				('heading', models.CharField(default='Digital Goods & Garments', max_length=200)),
				('heading_highlight', models.CharField(default='& Garments', max_length=120)),
				('description', models.TextField(default='A curated storefront is coming soon for premium website templates, practical digital assets, and limited garment drops built around the same design language as the client work.')),
				('primary_cta_label', models.CharField(default='Ask About The Shop', max_length=80)),
				('primary_cta_url', models.CharField(default='#contact', max_length=255)),
				('secondary_badge_label', models.CharField(default='Launching Soon', max_length=80)),
				('secondary_badge_icon', models.CharField(default='clock-3', max_length=50)),
				('updated_at', models.DateTimeField(auto_now=True)),
			],
			options={
				'verbose_name': 'Shop Section Settings',
				'verbose_name_plural': 'Shop Section Settings',
			},
		),
		migrations.RunPython(seed_shop_section_settings, migrations.RunPython.noop),
	]