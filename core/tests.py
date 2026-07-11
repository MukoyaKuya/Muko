from django.test import TestCase
from django.urls import reverse

from .models import ContactSubmission, FeaturedProject, ShopItem, ShopSectionSettings


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
		self.assertContains(response, 'Chat on WhatsApp')
		self.assertContains(response, 'Let\'s Work Together')
		self.assertContains(response, 'Send Message')

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

	def test_contact_form_get_returns_422(self):
		response = self.client.get(reverse('contact'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Send Message')

	def test_contact_form_submission_saves_and_returns_success(self):
		response = self.client.post(reverse('contact'), {
			'name': 'Test User',
			'email': 'test@example.com',
			'message': 'This is a test inquiry about a project.',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Message Sent')
		self.assertEqual(ContactSubmission.objects.count(), 1)
		submission = ContactSubmission.objects.first()
		self.assertEqual(submission.name, 'Test User')
		self.assertEqual(submission.email, 'test@example.com')

	def test_contact_form_submission_records_ip_and_user_agent(self):
		response = self.client.post(
			reverse('contact'),
			{
				'name': 'Bot User',
				'email': 'bot@example.com',
				'message': 'Hello from a test.',
			},
			HTTP_USER_AGENT='TestAgent/1.0',
			REMOTE_ADDR='127.0.0.1',
		)

		self.assertEqual(response.status_code, 200)
		submission = ContactSubmission.objects.first()
		self.assertEqual(submission.ip_address, '127.0.0.1')
		self.assertEqual(submission.user_agent, 'TestAgent/1.0')

	def test_contact_form_empty_fields_return_errors(self):
		response = self.client.post(reverse('contact'), {
			'name': '',
			'email': '',
			'message': '',
		})

		self.assertEqual(response.status_code, 422)
		self.assertContains(response, 'This field is required', status_code=422)
		self.assertEqual(ContactSubmission.objects.count(), 0)

	def test_contact_form_invalid_email_returns_error(self):
		response = self.client.post(reverse('contact'), {
			'name': 'Bad Email',
			'email': 'not-an-email',
			'message': 'Testing invalid email.',
		})

		self.assertEqual(response.status_code, 422)
		self.assertContains(response, 'Enter a valid email address', status_code=422)

	def test_contact_form_honeypot_rejects_bot_submission(self):
		response = self.client.post(reverse('contact'), {
			'name': 'Bot User',
			'email': 'bot@example.com',
			'message': 'This should not be accepted.',
			'website': 'https://spam.example',
		})

		self.assertEqual(response.status_code, 422)
		self.assertEqual(ContactSubmission.objects.count(), 0)
