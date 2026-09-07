from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.templatetags.static import static
from django.utils import timezone


# These formats are supported by modern browsers and can be served directly from
# the upload storage. Keep the same allow-list on every public image upload.
IMAGE_UPLOAD_EXTENSIONS = ['png', 'jpg', 'jpeg', 'jfif', 'webp', 'avif', 'gif']


class FeaturedProject(models.Model):
	FILTER_ALL = 'all'
	FILTER_WEB = 'web'
	FILTER_DESIGN = 'design'
	FILTER_GROUP_CHOICES = [
		(FILTER_WEB, 'Web'),
		(FILTER_DESIGN, 'Design'),
	]

	title = models.CharField(max_length=200)
	slug = models.SlugField(unique=True)
	category = models.CharField(max_length=120)
	filter_group = models.CharField(
		max_length=20,
		choices=FILTER_GROUP_CHOICES,
		default=FILTER_WEB,
		help_text='Controls which homepage filter chip shows this project.',
	)
	card_summary = models.CharField(max_length=200)
	headline = models.CharField(max_length=255)
	summary = models.TextField()
	hero_image = models.CharField(
		max_length=255,
		blank=True,
		help_text='Path relative to static/, for example img/work1.png (legacy — prefer uploading below).',
	)
	hero_image_upload = models.FileField(
		upload_to='projects/',
		blank=True,
		null=True,
		validators=[FileExtensionValidator(IMAGE_UPLOAD_EXTENSIONS)],
		help_text='Upload a project screenshot or hero image. Overrides the legacy path above. Supports PNG, JPG/JFIF, WebP, AVIF, and GIF.',
	)
	live_url = models.URLField(
		blank=True,
		help_text='Optional live URL of the website, e.g. https://example.com',
	)
	challenge = models.TextField()
	approach = models.TextField()
	outcome = models.TextField()
	services = models.TextField(help_text='One service per line, in the order you want them displayed.')
	stack = models.TextField(help_text='One stack item per line, for the chips on the detail page.')
	display_order = models.PositiveIntegerField(default=0)
	is_published = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['display_order', 'title']

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('project_detail', kwargs={'slug': self.slug})

	@property
	def services_list(self):
		return [item.strip() for item in self.services.splitlines() if item.strip()]

	@property
	def stack_list(self):
		return [item.strip() for item in self.stack.splitlines() if item.strip()]

	def get_all_images(self):
		"""Return all images: hero first (upload preferred, legacy fallback), then gallery images in order."""
		images = []
		if self.hero_image_upload:
			images.append(self.hero_image_upload.url)
		elif self.hero_image:
			images.append(static(self.hero_image))
		images += [img.image.url for img in self.gallery_images.all()]
		return images


class ProjectImage(models.Model):
	project = models.ForeignKey(
		FeaturedProject,
		on_delete=models.CASCADE,
		related_name='gallery_images',
	)
	image = models.FileField(
		upload_to='projects/gallery/',
		validators=[FileExtensionValidator(IMAGE_UPLOAD_EXTENSIONS)],
	)
	caption = models.CharField(max_length=200, blank=True)
	display_order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['display_order']

	def __str__(self):
		return f'{self.project.title} — image {self.display_order}'


class ShopCategory(models.Model):
	"""A top-level, public-facing catalogue category."""

	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	description = models.TextField(
		help_text='Short introduction shown on the catalogue landing page.',
	)
	icon = models.CharField(
		max_length=50,
		default='package',
		help_text='Lucide icon name, for example shirt, code-2, or blocks.',
	)
	image_upload = models.FileField(
		upload_to='shop/categories/',
		blank=True,
		null=True,
		validators=[FileExtensionValidator(IMAGE_UPLOAD_EXTENSIONS)],
		help_text='Optional category image. Supports PNG, JPG/JFIF, WebP, AVIF, and GIF.',
	)
	display_order = models.PositiveIntegerField(default=0)
	is_published = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['display_order', 'name']
		verbose_name = 'Shop category'
		verbose_name_plural = 'Shop categories'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('shop_category', kwargs={'slug': self.slug})


class ShopItem(models.Model):
	catalog_category = models.ForeignKey(
		ShopCategory,
		on_delete=models.PROTECT,
		related_name='items',
		help_text='The catalogue category where this item appears.',
	)
	title = models.CharField(max_length=150)
	category = models.CharField(
		max_length=80,
		blank=True,
		verbose_name='Item type',
		help_text='Optional smaller label, for example Garment, Branded pen, or Web development.',
	)
	icon = models.CharField(
		max_length=50,
		help_text='Lucide icon name, for example shopping-bag, package, or shirt.',
	)
	image_upload = models.FileField(
		upload_to='shop/',
		blank=True,
		null=True,
		validators=[FileExtensionValidator(IMAGE_UPLOAD_EXTENSIONS)],
		help_text='Upload a shop image. This is used first when present. Supports PNG, JPG/JFIF, WebP, AVIF, and GIF.',
	)
	image_path = models.CharField(
		max_length=255,
		blank=True,
		help_text='Optional legacy path relative to static/, for example img/work3.png.',
	)
	link_url = models.CharField(
		max_length=255,
		blank=True,
		help_text='Optional destination URL for this item. Leave blank to use the main WhatsApp contact link.',
	)
	price_label = models.CharField(
		max_length=80,
		blank=True,
		help_text='Optional display text, for example “From KES 2,500” or “Request a quote”.',
	)
	cta_label = models.CharField(
		max_length=80,
		default='Ask about this item',
		help_text='Label shown on the item enquiry button.',
	)
	description = models.TextField()
	display_order = models.PositiveIntegerField(default=0)
	is_published = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['display_order', 'title']

	def __str__(self):
		return self.title

	@property
	def image_url(self):
		if self.image_upload:
			return self.image_upload.url
		if self.image_path:
			return static(self.image_path)
		return ''


class ShopSectionSettings(models.Model):
	eyebrow = models.CharField(max_length=80, default='Shop')
	heading = models.CharField(max_length=200, default='Karibu My Shop')
	heading_highlight = models.CharField(max_length=120, default='& Garments')
	description = models.TextField(
		default='A curated storefront is coming soon for premium website templates, practical digital assets, and limited garment drops built around the same design language as the client work.',
	)
	primary_cta_label = models.CharField(max_length=80, default='Ask About The Shop')
	primary_cta_url = models.CharField(
		max_length=255,
		default='https://wa.me/254717157165?text=Hi%20Muko%2C%20I%27d%20like%20to%20talk%20about%20a%20project.',
	)
	secondary_badge_label = models.CharField(max_length=80, default='Launching Soon')
	secondary_badge_icon = models.CharField(max_length=50, default='clock-3')
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Shop Section Settings'
		verbose_name_plural = 'Shop Section Settings'

	def __str__(self):
		return 'Shop Section Settings'

	def save(self, *args, **kwargs):
		if not self.pk and ShopSectionSettings.objects.exists():
			raise ValueError('Only one ShopSectionSettings instance is allowed.')
		super().save(*args, **kwargs)


class ContactSubmission(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField(max_length=254)
	message = models.TextField(max_length=2000)
	ip_address = models.GenericIPAddressField(blank=True, null=True)
	user_agent = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.name} <{self.email}>'


class Visitor(models.Model):
	"""An anonymized visitor record keyed by a one-way hash of the IP address."""

	ip_hash = models.CharField(max_length=64, unique=True, db_index=True)
	visit_count = models.PositiveBigIntegerField(default=1)
	first_seen = models.DateTimeField(auto_now_add=True)
	last_seen = models.DateTimeField()
	last_path = models.CharField(max_length=255, blank=True)
	user_agent = models.CharField(max_length=500, blank=True)
	device_type = models.CharField(max_length=50, default='Desktop', help_text="Mobile, Tablet, Desktop, or Bot/Crawler.")
	region = models.CharField(max_length=100, default='Unknown', help_text="Detected region or country.")
	is_bot = models.BooleanField(default=False, help_text="True if this visitor is identified as a search crawler or bot.")

	class Meta:
		ordering = ['-last_seen']

	def __str__(self):
		return f'Visitor {self.ip_hash[:12]}…'

	@property
	def fingerprint(self):
		return f'{self.ip_hash[:12]}…'


class VisitLog(models.Model):
	visitor = models.ForeignKey(
		Visitor,
		on_delete=models.CASCADE,
		related_name='logs',
	)
	timestamp = models.DateTimeField(default=timezone.now)
	path = models.CharField(max_length=255)
	is_bot = models.BooleanField(default=False)

	class Meta:
		ordering = ['-timestamp']
		indexes = [
			models.Index(fields=['timestamp', 'is_bot']),
		]

	def __str__(self):
		return f"{'Bot' if self.is_bot else 'User'} visit at {self.timestamp}"



class PortfolioSettings(models.Model):
	cv_file = models.FileField(
		upload_to='documents/',
		validators=[FileExtensionValidator(['pdf'])],
		help_text='Upload your current CV as a PDF.',
	)
	cv_label = models.CharField(max_length=40, default='View CV')
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Portfolio Settings'
		verbose_name_plural = 'Portfolio Settings'

	def __str__(self):
		return 'Portfolio Settings'

	def save(self, *args, **kwargs):
		if not self.pk and PortfolioSettings.objects.exists():
			raise ValueError('Only one PortfolioSettings instance is allowed.')
		super().save(*args, **kwargs)


class SiteContentSettings(models.Model):
	hero_eyebrow = models.CharField(max_length=80, default="Hello, I'm")
	hero_description = models.CharField(
		max_length=240,
		default="Let's design and build digital experiences that convert, engage, and stand out.",
	)
	hero_cta_label = models.CharField(max_length=60, default='View My Work')
	services_eyebrow = models.CharField(max_length=80, default='My Expertise')
	services_heading = models.CharField(max_length=100, default='Services')
	services_heading_highlight = models.CharField(max_length=100, default='& Solutions')
	services_intro = models.CharField(
		max_length=240,
		default='Select a service to see what the engagement includes, how I approach it, and what you can expect.',
	)
	work_eyebrow = models.CharField(max_length=80, default='Selected Projects')
	work_heading = models.CharField(max_length=100, default='Featured')
	work_heading_highlight = models.CharField(max_length=100, default='Works')
	contact_eyebrow = models.CharField(max_length=80, default='Get in touch')
	contact_heading = models.CharField(max_length=100, default="Let's")
	contact_heading_highlight = models.CharField(max_length=100, default='Collaborate')
	contact_intro = models.TextField(
		default="Have a project in mind? Looking for a partner to build something impactful? Message me on WhatsApp and let's start the conversation where it is fastest.",
	)
	footer_text = models.CharField(max_length=160, default='MUKO. Built with Passion.')
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Site Content Settings'
		verbose_name_plural = 'Site Content Settings'

	def __str__(self):
		return 'Site Content Settings'

	def save(self, *args, **kwargs):
		if not self.pk and SiteContentSettings.objects.exists():
			raise ValueError('Only one SiteContentSettings instance is allowed.')
		super().save(*args, **kwargs)


class Service(models.Model):
	site_content = models.ForeignKey(
		SiteContentSettings,
		on_delete=models.CASCADE,
		related_name='services',
	)
	title = models.CharField(max_length=150)
	slug = models.SlugField(
		max_length=50,
		help_text="Unique identifier for frontend script logic, e.g., 'web', 'design', 'platforms', 'cloud', 'seo'",
	)
	icon = models.CharField(
		max_length=50,
		help_text="Lucide icon name, e.g., 'code-2', 'pen-tool', 'layout-grid', 'cloud', 'search'",
	)
	short_description = models.TextField(help_text="Brief description displayed on the main card.")
	description = models.TextField(help_text="Detailed description displayed in the modal.")
	includes = models.TextField(help_text="What the service includes. One item per line.")
	outcomes = models.TextField(help_text="Typical outcomes of the service. One item per line.")
	tags = models.CharField(
		max_length=255,
		blank=True,
		help_text="Optional tags, comma-separated. E.g., 'AWS, Azure' for cloud infrastructure.",
	)
	column_span = models.PositiveIntegerField(
		default=2,
		choices=[(2, '2 Columns'), (3, '3 Columns'), (6, 'Full Width')],
		help_text="Card width in the grid (total grid is 6 columns).",
	)
	show_bg_icon = models.BooleanField(
		default=False,
		help_text="Show a large semi-transparent icon in the card background.",
	)
	display_order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['display_order', 'id']

	def __str__(self):
		return self.title

	@property
	def includes_list(self):
		return [item.strip() for item in self.includes.splitlines() if item.strip()]

	@property
	def outcomes_list(self):
		return [item.strip() for item in self.outcomes.splitlines() if item.strip()]

	@property
	def tags_list(self):
		if not self.tags:
			return []
		return [t.strip() for t in self.tags.split(',') if t.strip()]

	@property
	def icon_size_class(self):
		if self.icon in ('code-2', 'cloud'):
			return 'h-10 w-10'
		return 'h-9 w-9'

	@property
	def max_width_class(self):
		if self.slug == 'web':
			return 'max-w-sm'
		elif self.slug == 'cloud':
			return 'max-w-md'
		elif self.slug == 'seo':
			return 'max-w-xl'
		return ''

	@property
	def layout_class(self):
		if self.tags:
			return 'flex h-full flex-col justify-between gap-5 text-left md:flex-row md:items-end'
		return 'block text-left'
