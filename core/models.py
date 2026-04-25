from django.db import models
from django.templatetags.static import static


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
	hero_image_upload = models.ImageField(
		upload_to='projects/',
		blank=True,
		null=True,
		help_text='Upload a project screenshot or hero image. Overrides the legacy path above.',
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
	image = models.ImageField(upload_to='projects/gallery/')
	caption = models.CharField(max_length=200, blank=True)
	display_order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['display_order']

	def __str__(self):
		return f'{self.project.title} — image {self.display_order}'


class ShopItem(models.Model):
	title = models.CharField(max_length=150)
	category = models.CharField(max_length=80)
	icon = models.CharField(
		max_length=50,
		help_text='Lucide icon name, for example shopping-bag, package, or shirt.',
	)
	image_upload = models.ImageField(
		upload_to='shop/',
		blank=True,
		null=True,
		help_text='Upload a shop image. This is used first when present.',
	)
	image_path = models.CharField(
		max_length=255,
		blank=True,
		help_text='Optional legacy path relative to static/, for example img/work3.png.',
	)
	link_url = models.CharField(
		max_length=255,
		blank=True,
		help_text='Optional destination URL for the card CTA.',
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
