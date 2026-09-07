from django.test import TestCase
from django.urls import reverse

from .models import ShopCategory, ShopItem


class ShopCatalogueTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		ShopItem.objects.all().delete()
		ShopCategory.objects.all().delete()
		cls.branding = ShopCategory.objects.create(
			name='Branding',
			slug='branding',
			description='Garments and branded goods.',
			icon='palette',
			display_order=10,
		)
		cls.software = ShopCategory.objects.create(
			name='Software Development',
			slug='software-development',
			description='Digital products and systems.',
			icon='code-2',
			display_order=20,
		)
		ShopItem.objects.create(
			catalog_category=cls.branding,
			title='Branded T-shirt',
			category='Garment',
			icon='shirt',
			description='A custom shirt for your team.',
			price_label='Request a quote',
		)
		ShopItem.objects.create(
			catalog_category=cls.software,
			title='Custom Desktop App',
			category='Desktop application',
			icon='monitor-cog',
			description='A tailored desktop workflow.',
		)
		ShopItem.objects.create(
			catalog_category=cls.branding,
			title='Hidden sample',
			category='Garment',
			icon='shirt',
			description='Not public.',
			is_published=False,
		)

	def test_catalogue_landing_lists_published_categories(self):
		response = self.client.get(reverse('shop_home'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Branding')
		self.assertContains(response, 'Software Development')
		self.assertContains(response, reverse('shop_category', kwargs={'slug': 'branding'}))

	def test_category_page_lists_only_its_published_items(self):
		response = self.client.get(reverse('shop_category', kwargs={'slug': 'branding'}))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Branded T-shirt')
		self.assertContains(response, 'Request a quote')
		self.assertNotContains(response, 'Custom Desktop App')
		self.assertNotContains(response, 'Hidden sample')

	def test_unpublished_category_returns_not_found(self):
		self.software.is_published = False
		self.software.save(update_fields=['is_published'])

		response = self.client.get(reverse('shop_category', kwargs={'slug': 'software-development'}))

		self.assertEqual(response.status_code, 404)
