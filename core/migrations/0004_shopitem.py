from django.db import migrations, models


def seed_shop_items(apps, schema_editor):
	ShopItem = apps.get_model('core', 'ShopItem')
	items = [
		{
			'title': 'Website Templates',
			'category': 'Templates',
			'icon': 'layout-template',
			'description': 'Ready-to-launch layouts for portfolios, landing pages, and business sites with sharp structure and modern visual rhythm.',
			'display_order': 1,
			'is_published': True,
		},
		{
			'title': 'Digital Assets',
			'category': 'Assets',
			'icon': 'package',
			'description': 'UI kits, presentation packs, creative resources, and reusable design systems for builders who want to move faster.',
			'display_order': 2,
			'is_published': True,
		},
		{
			'title': 'Side-Hustle Apparel',
			'category': 'Garments',
			'icon': 'shirt',
			'description': 'Small-batch wearable pieces tied to the brand, the process, and the culture around making things that look intentional.',
			'display_order': 3,
			'is_published': True,
		},
	]

	for payload in items:
		ShopItem.objects.update_or_create(title=payload['title'], defaults=payload)


class Migration(migrations.Migration):

	dependencies = [
		('core', '0003_featuredproject_filter_group'),
	]

	operations = [
		migrations.CreateModel(
			name='ShopItem',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('title', models.CharField(max_length=150)),
				('category', models.CharField(max_length=80)),
				('icon', models.CharField(help_text='Lucide icon name, for example shopping-bag, package, or shirt.', max_length=50)),
				('description', models.TextField()),
				('display_order', models.PositiveIntegerField(default=0)),
				('is_published', models.BooleanField(default=True)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
			],
			options={
				'ordering': ['display_order', 'title'],
			},
		),
		migrations.RunPython(seed_shop_items, migrations.RunPython.noop),
	]