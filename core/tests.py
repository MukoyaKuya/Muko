from django.test import TestCase
from django.urls import reverse

from .models import FeaturedProject, ShopItem, ShopSectionSettings


class PortfolioPageTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		FeaturedProject.objects.all().delete()
		ShopItem.objects.all().delete()
		ShopSectionSettings.objects.all().delete()
		FeaturedProject.objects.create(
			title='Nexus Fintech',
			slug='nexus-fintech',
			category='Dashboard / Product Design',
			filter_group='web',
			card_summary='A calmer fintech operations dashboard concept with clearer hierarchy.',
			headline='A sharper fintech operations dashboard built for trust, speed, and daily decision-making.',
			summary='Nexus Fintech rethinks a cluttered internal dashboard into a calmer product surface.',
			hero_image='img/work1.png',
			challenge='Challenge copy',
			approach='Approach copy',
			outcome='Outcome copy',
			services='UX strategy\nDashboard design',
			stack='Django\nHTMX',
			display_order=1,
		)
		FeaturedProject.objects.create(
			title='Velvet Estates',
			slug='velvet-estates',
			category='Luxury Landing Page',
			filter_group='design',
			card_summary='A premium real-estate landing page concept with stronger inquiry flow.',
			headline='A real estate launch page designed to feel cinematic, premium, and conversion-ready.',
			summary='Velvet Estates explores a more editorial, emotionally-led web experience.',
			hero_image='img/work2.png',
			challenge='Challenge copy',
			approach='Approach copy',
			outcome='Outcome copy',
			services='Creative direction\nLanding page design',
			stack='Django\nGSAP',
			display_order=2,
		)
		ShopItem.objects.create(
			title='Website Templates',
			category='Templates',
			icon='layout-template',
			image_path='img/work3.png',
			link_url='https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.',
			description='Ready-to-launch layouts for portfolios, landing pages, and business sites.',
			display_order=1,
		)
		ShopSectionSettings.objects.create(
			eyebrow='Shop',
			heading='Digital Goods',
			heading_highlight='& Garments',
			description='Shop intro copy',
			primary_cta_label='Ask About The Shop',
			primary_cta_url='https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.',
			secondary_badge_label='Launching Soon',
			secondary_badge_icon='clock-3',
		)

	def test_homepage_uses_real_social_links(self):
		response = self.client.get(reverse('home'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'https://github.com/MukoyaKuya')
		self.assertContains(response, 'https://www.linkedin.com/in/mukoya-kuya/')
		self.assertContains(response, 'https://x.com/KuyaMukoya')
		self.assertContains(response, 'A calmer fintech operations dashboard concept with clearer hierarchy.')
		self.assertContains(response, '?category=web')
		self.assertContains(response, '?category=design')
		self.assertContains(response, 'Website Templates')
		self.assertContains(response, 'layout-template')
		self.assertContains(response, 'img/work3.png')
		self.assertContains(response, 'Shop intro copy')
		self.assertContains(response, 'Ask About The Shop')
		self.assertContains(response, 'https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.')
		self.assertContains(response, '0717 157 165')
		self.assertContains(response, 'Chat On WhatsApp')

	def test_homepage_can_filter_featured_projects_by_category(self):
		response = self.client.get(reverse('home'), {'category': 'design'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Velvet Estates')
		self.assertNotContains(response, 'Nexus Fintech')

	def test_unknown_filter_falls_back_to_all_projects(self):
		response = self.client.get(reverse('home'), {'category': 'unknown'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Velvet Estates')
		self.assertContains(response, 'Nexus Fintech')

	def test_htmx_filter_request_returns_partial_markup(self):
		response = self.client.get(
			reverse('home'),
			{'category': 'design'},
			HTTP_HX_REQUEST='true',
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'id="featured-projects-panel"')
		self.assertContains(response, 'Velvet Estates')
		self.assertNotContains(response, '<!DOCTYPE html>', html=False)

	def test_project_detail_route_renders_case_study(self):
		response = self.client.get(reverse('project_detail', args=['nexus-fintech']))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Nexus Fintech')
		self.assertContains(response, 'A sharper fintech operations dashboard built for trust, speed, and daily decision-making.')
		self.assertContains(response, 'Dashboard design')
		self.assertContains(response, 'https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.')

	def test_unknown_project_slug_returns_404(self):
		response = self.client.get(reverse('project_detail', args=['missing-project']))

		self.assertEqual(response.status_code, 404)
