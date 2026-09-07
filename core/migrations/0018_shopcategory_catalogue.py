# Generated manually for the catalogue upgrade.

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def seed_catalogue_categories(apps, schema_editor):
    ShopCategory = apps.get_model('core', 'ShopCategory')
    ShopItem = apps.get_model('core', 'ShopItem')

    category_data = [
        {
            'name': 'Branding',
            'slug': 'branding',
            'description': 'Branded garments, pens, merchandise, and practical business identity assets.',
            'icon': 'palette',
            'display_order': 10,
            'is_published': True,
        },
        {
            'name': 'Software Development',
            'slug': 'software-development',
            'description': 'Web development, custom desktop apps, digital platforms, and business systems.',
            'icon': 'code-2',
            'display_order': 20,
            'is_published': True,
        },
        {
            'name': 'APIs & Services',
            'slug': 'apis-services',
            'description': 'Transcription, video editing, animation, templates, and other ready-to-use digital services.',
            'icon': 'blocks',
            'display_order': 30,
            'is_published': True,
        },
    ]

    categories = {}
    for data in category_data:
        category, _ = ShopCategory.objects.update_or_create(
            slug=data['slug'], defaults=data,
        )
        categories[category.slug] = category

    for item in ShopItem.objects.filter(catalog_category__isnull=True):
        label = f'{item.title} {item.category}'.lower()
        if any(word in label for word in ('apparel', 'garment', 'brand', 'pen', 'merchandise')):
            target = categories['branding']
        elif any(word in label for word in ('template', 'asset', 'api', 'transcri', 'video', 'animation')):
            target = categories['apis-services']
        else:
            target = categories['software-development']
        item.catalog_category = target
        item.save(update_fields=['catalog_category'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_visitor_device_type_visitor_is_bot_visitor_region_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(help_text='Short introduction shown on the catalogue landing page.')),
                ('icon', models.CharField(default='package', help_text='Lucide icon name, for example shirt, code-2, or blocks.', max_length=50)),
                ('image_upload', models.FileField(blank=True, help_text='Optional category image. It appears on the catalogue category card.', null=True, upload_to='shop/categories/', validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg', 'webp', 'gif'])])),
                ('display_order', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Shop category',
                'verbose_name_plural': 'Shop categories',
                'ordering': ['display_order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='shopitem',
            name='catalog_category',
            field=models.ForeignKey(blank=True, help_text='The catalogue category where this item appears.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.shopcategory'),
        ),
        migrations.AddField(
            model_name='shopitem',
            name='price_label',
            field=models.CharField(blank=True, help_text='Optional display text, for example “From KES 2,500” or “Request a quote”.', max_length=80),
        ),
        migrations.AddField(
            model_name='shopitem',
            name='cta_label',
            field=models.CharField(default='Ask about this item', help_text='Label shown on the item enquiry button.', max_length=80),
        ),
        migrations.AlterField(
            model_name='shopitem',
            name='category',
            field=models.CharField(blank=True, help_text='Optional smaller label, for example Garment, Branded pen, or Web development.', max_length=80, verbose_name='Item type'),
        ),
        migrations.RunPython(seed_catalogue_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='shopitem',
            name='catalog_category',
            field=models.ForeignKey(help_text='The catalogue category where this item appears.', on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.shopcategory'),
        ),
    ]
