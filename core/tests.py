from datetime import timedelta
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from unittest.mock import Mock, patch

from .models import ContactSubmission, FeaturedProject, ShopCategory, ShopItem, ShopSectionSettings


class ImageUploadValidationTests(TestCase):
	def test_featured_project_accepts_avif_and_jfif_uploads(self):
		field = FeaturedProject._meta.get_field('hero_image_upload')

		for filename in ('project.avif', 'camera-export.jfif'):
			with self.subTest(filename=filename):
				field.run_validators(SimpleUploadedFile(filename, b'image-content'))

	def test_featured_project_rejects_non_image_extensions(self):
		field = FeaturedProject._meta.get_field('hero_image_upload')

		with self.assertRaises(ValidationError):
			field.run_validators(SimpleUploadedFile('malware.exe', b'not an image'))


class PortfolioPageTests(TestCase):
	def setUp(self):
		cache.clear()

	@classmethod
	def setUpTestData(cls):
		FeaturedProject.objects.all().delete()
		ShopItem.objects.all().delete()
		ShopCategory.objects.all().delete()
		ShopSectionSettings.objects.all().delete()
		cls.shop_category = ShopCategory.objects.create(
			name='Software Development',
			slug='software-development',
			description='Web development, desktop apps, and platforms.',
			icon='code-2',
			display_order=10,
		)
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
			catalog_category=cls.shop_category,
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
		self.assertContains(response, 'Software Development')
		self.assertContains(response, reverse('shop_category', kwargs={'slug': 'software-development'}))
		self.assertContains(response, 'Browse all categories')
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

	def test_contact_form_does_not_store_ip_and_keeps_user_agent(self):
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
		self.assertIsNone(submission.ip_address)
		self.assertEqual(submission.user_agent, 'TestAgent/1.0')

	@override_settings(CONTACT_RATE_LIMIT=1, CONTACT_RATE_LIMIT_WINDOW_SECONDS=3600)
	def test_contact_form_rate_limits_repeated_requests(self):
		payload = {
			'name': 'Test User',
			'email': 'test@example.com',
			'message': 'This is a test inquiry about a project.',
		}
		self.assertEqual(self.client.post(reverse('contact'), payload, REMOTE_ADDR='203.0.113.90').status_code, 200)
		response = self.client.post(reverse('contact'), payload, REMOTE_ADDR='203.0.113.90')

		self.assertEqual(response.status_code, 429)
		self.assertContains(response, 'Too many messages', status_code=429)

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


class VisitorTrackingTests(TestCase):
	def test_tracks_unique_ip_without_storing_raw_address(self):
		response = self.client.get(
			reverse('home'),
			REMOTE_ADDR='203.0.113.42',
			HTTP_USER_AGENT='Portfolio Browser',
		)

		self.assertEqual(response.status_code, 200)
		from .models import Visitor
		visitor = Visitor.objects.get()
		self.assertEqual(visitor.visit_count, 1)
		self.assertNotIn('203.0.113.42', visitor.ip_hash)
		self.assertEqual(visitor.last_path, '/')

	def test_repeat_requests_in_same_session_are_deduplicated(self):
		from .models import Visitor
		for _ in range(2):
			self.client.get(
				reverse('home'),
				REMOTE_ADDR='203.0.113.43',
				HTTP_USER_AGENT='Portfolio Browser',
			)

		self.assertEqual(Visitor.objects.get().visit_count, 1)

	def test_same_ip_across_sessions_increments_visit_count(self):
		from django.test import Client
		from .models import Visitor

		for _ in range(2):
			Client().get(
				reverse('home'),
				REMOTE_ADDR='203.0.113.44',
				HTTP_USER_AGENT='Portfolio Browser',
			)

		self.assertEqual(Visitor.objects.get().visit_count, 2)

	def test_admin_requests_are_not_tracked(self):
		from .models import Visitor
		self.client.get('/admin/', REMOTE_ADDR='203.0.113.45')
		self.assertFalse(Visitor.objects.exists())

	def test_bots_are_not_tracked_by_default(self):
		from .models import Visitor
		self.client.get(
			reverse('home'),
			REMOTE_ADDR='203.0.113.50',
			HTTP_USER_AGENT='Googlebot/2.1 (+http://www.google.com/bot.html)',
		)
		self.assertFalse(Visitor.objects.exists())

	@override_settings(TRACK_BOT_VISITS=True)
	def test_visitor_device_region_and_bot_classification(self):
		from .models import Visitor, VisitLog

		# Test bot visitor
		self.client.get(
			reverse('home'),
			REMOTE_ADDR='203.0.113.50',
			HTTP_USER_AGENT='Googlebot/2.1 (+http://www.google.com/bot.html)',
		)
		bot_visitor = Visitor.objects.get(device_type='Bot/Crawler')
		self.assertTrue(bot_visitor.is_bot)
		self.assertEqual(VisitLog.objects.filter(is_bot=True).count(), 1)

		# Test mobile visitor
		self.client.get(
			reverse('home'),
			REMOTE_ADDR='203.0.113.51',
			HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
		)
		mobile_visitor = Visitor.objects.exclude(device_type='Bot/Crawler').get()
		self.assertEqual(mobile_visitor.device_type, 'Mobile')
		self.assertFalse(mobile_visitor.is_bot)
		self.assertEqual(VisitLog.objects.filter(is_bot=False).count(), 1)

	@override_settings(GEOIP_DATABASE_PATH='/tmp/GeoLite2-Country.mmdb')
	@patch('core.geoip._get_reader')
	def test_records_country_from_local_geoip_database(self, reader_factory):
		from .models import Visitor

		reader = Mock()
		reader.country.return_value.country.name = 'Kenya'
		reader_factory.return_value = reader

		self.client.get(
			reverse('home'),
			REMOTE_ADDR='8.8.8.8',
			HTTP_USER_AGENT='Portfolio Browser',
		)

		self.assertEqual(Visitor.objects.get().region, 'Kenya')

	@override_settings(GEOIP_DATABASE_PATH='/tmp/GeoLite2-Country.mmdb')
	@patch('core.geoip._get_reader')
	def test_enriches_an_unknown_visitor_when_they_return(self, reader_factory):
		from django.test import Client
		from django.utils.crypto import salted_hmac
		from .models import Visitor

		reader = Mock()
		reader.country.return_value.country.name = 'Uganda'
		reader_factory.return_value = reader
		Visitor.objects.create(
			ip_hash=salted_hmac('muko-visitor-ip', '8.8.4.4').hexdigest(),
			last_seen=timezone.now() - timedelta(hours=1),
			region='Unknown',
		)

		Client().get(
			reverse('home'),
			REMOTE_ADDR='8.8.4.4',
			HTTP_USER_AGENT='Portfolio Browser',
		)

		self.assertEqual(Visitor.objects.get().region, 'Uganda')


class DiscoverabilityAndSecurityTests(TestCase):
	def test_public_pages_include_seo_metadata_and_security_headers(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, 'name="description"')
		self.assertContains(response, 'rel="canonical"')
		self.assertIn('Content-Security-Policy', response)
		self.assertIn('Permissions-Policy', response)
		self.assertIn("script-src 'self' 'nonce-", response['Content-Security-Policy'])

	def test_robots_and_sitemap_are_available(self):
		robots = self.client.get(reverse('robots_txt'))
		sitemap = self.client.get(reverse('sitemap'))

		self.assertEqual(robots.status_code, 200)
		self.assertContains(robots, 'Sitemap:')
		self.assertEqual(sitemap.status_code, 200)
		self.assertContains(sitemap, '<urlset', html=False)



class PortfolioCvTests(TestCase):
	def test_cv_button_is_hidden_until_pdf_is_configured(self):
		response = self.client.get(reverse('home'))
		self.assertNotContains(response, 'aria-label="View CV"')

	def test_cv_button_links_to_admin_managed_pdf(self):
		from .models import PortfolioSettings
		PortfolioSettings.objects.create(
			cv_file='documents/muko-cv.pdf',
			cv_label='Download CV',
		)

		response = self.client.get(reverse('home'))

		self.assertContains(response, '/media/documents/muko-cv.pdf')
		self.assertContains(response, 'aria-label="Download CV"')
		self.assertContains(response, 'data-lucide="file-text"')


class SiteContentSettingsTests(TestCase):
	def test_admin_managed_copy_renders_on_homepage(self):
		from .models import SiteContentSettings
		SiteContentSettings.objects.all().delete()
		SiteContentSettings.objects.create(
			hero_eyebrow='Hello from admin',
			hero_description='Custom hero description.',
			hero_cta_label='See Projects',
			services_eyebrow='Capabilities',
			services_heading='What I',
			services_heading_highlight='Deliver',
			services_intro='Custom services introduction.',
			work_eyebrow='Recent Work',
			work_heading='Selected',
			work_heading_highlight='Projects',
			contact_eyebrow='Start a conversation',
			contact_heading='Build',
			contact_heading_highlight='Together',
			contact_intro='Custom contact introduction.',
			footer_text='Custom footer text.',
		)

		response = self.client.get(reverse('home'))


		self.assertContains(response, 'Hello from admin')
		self.assertContains(response, 'Custom hero description.')
		self.assertContains(response, 'Custom services introduction.')
		self.assertContains(response, 'Custom contact introduction.')
		self.assertContains(response, 'Custom footer text.')

	def test_dynamic_services_render_on_homepage(self):
		from .models import SiteContentSettings, Service
		Service.objects.all().delete()
		SiteContentSettings.objects.all().delete()

		site_content = SiteContentSettings.objects.create(
			services_eyebrow='Dynamic Capabilities',
			services_intro='See our dynamic list of services.'
		)

		service = Service.objects.create(
			site_content=site_content,
			title='Hyper Scaler Dev',
			slug='hyperscaler',
			icon='cloud-lightning',
			short_description='We build hyperscale software.',
			description='A detailed overview of hyperscale development.',
			includes='Feature 1\nFeature 2',
			outcomes='Outcome 1\nOutcome 2',
			tags='Docker, Kubernetes',
			column_span=3,
			show_bg_icon=True,
			display_order=5
		)

		# Test properties
		self.assertEqual(service.includes_list, ['Feature 1', 'Feature 2'])
		self.assertEqual(service.outcomes_list, ['Outcome 1', 'Outcome 2'])
		self.assertEqual(service.tags_list, ['Docker', 'Kubernetes'])

		response = self.client.get(reverse('home'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Hyper Scaler Dev')
		self.assertContains(response, 'We build hyperscale software.')
		self.assertContains(response, 'Docker')
		self.assertContains(response, 'Kubernetes')
		# Check that JS serviceDetails object is populated
		self.assertContains(response, '"hyperscaler"')
		self.assertContains(response, 'Hyper Scaler Dev')
		self.assertContains(response, 'cloud-lightning')
		# The JSON script must contain an object, not a JSON string.  The modal
		# click handler indexes this value by service slug in the browser.
		self.assertNotContains(response, '&quot;{')
