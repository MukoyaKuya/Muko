from django import forms
from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html

from .models import ContactSubmission, FeaturedProject, ProjectImage, ShopCategory, ShopItem, ShopSectionSettings, Visitor, PortfolioSettings, SiteContentSettings, Service, VisitLog


admin.site.site_header = 'Muko Admin'
admin.site.site_title = 'Muko Admin'
admin.site.index_title = 'Content Control Center'


class FeaturedProjectAdminForm(forms.ModelForm):
	remove_uploaded_hero_image = forms.BooleanField(
		required=False,
		label='Remove uploaded hero image',
		help_text='Delete the current uploaded hero image and fall back to the legacy static path if one is set.',
	)

	class Meta:
		model = FeaturedProject
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if not self.instance or not self.instance.hero_image_upload:
			self.fields['remove_uploaded_hero_image'].widget = forms.HiddenInput()

	def save(self, commit=True):
		instance = super().save(commit=False)
		should_remove_uploaded_image = (
			self.cleaned_data.get('remove_uploaded_hero_image')
			and not self.files.get(self.add_prefix('hero_image_upload'))
		)

		if should_remove_uploaded_image and instance.hero_image_upload:
			instance.hero_image_upload.delete(save=False)
			instance.hero_image_upload = None

		if commit:
			instance.save()
			self.save_m2m()

		return instance


class ShopItemAdminForm(forms.ModelForm):
	remove_uploaded_image = forms.BooleanField(
		required=False,
		label='Remove uploaded image',
		help_text='Delete the current uploaded image and use the optional legacy static path if set.',
	)

	class Meta:
		model = ShopItem
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if not self.instance or not self.instance.image_upload:
			self.fields['remove_uploaded_image'].widget = forms.HiddenInput()

	def save(self, commit=True):
		instance = super().save(commit=False)
		should_remove_uploaded_image = (
			self.cleaned_data.get('remove_uploaded_image')
			and not self.files.get(self.add_prefix('image_upload'))
		)

		if should_remove_uploaded_image and instance.image_upload:
			instance.image_upload.delete(save=False)
			instance.image_upload = None

		if commit:
			instance.save()
			self.save_m2m()

		return instance


class ProjectImageInline(admin.TabularInline):
	model = ProjectImage
	extra = 1
	fields = ('image', 'caption', 'display_order')
	ordering = ('display_order',)


@admin.register(FeaturedProject)
class FeaturedProjectAdmin(admin.ModelAdmin):
	form = FeaturedProjectAdminForm
	list_display = ('title', 'category', 'filter_group', 'display_order', 'is_published', 'image_preview')
	list_editable = ('filter_group', 'display_order', 'is_published')
	prepopulated_fields = {'slug': ('title',)}
	search_fields = ('title', 'category', 'headline', 'summary')
	list_filter = ('is_published', 'filter_group')
	list_per_page = 25
	save_on_top = True
	readonly_fields = ('image_preview',)
	inlines = [ProjectImageInline]
	fieldsets = (
		('Portfolio Card', {
			'fields': ('title', 'slug', 'category', 'filter_group', 'card_summary', 'live_url'),
		}),
		('Hero Image', {
			'fields': ('hero_image_upload', 'remove_uploaded_hero_image', 'image_preview', 'hero_image'),
			'description': 'Upload a screenshot or hero image. The uploaded file takes priority; the legacy path is a fallback for existing projects.',
		}),
		('Case Study Story', {
			'fields': ('headline', 'summary', 'challenge', 'approach', 'outcome', 'services', 'stack'),
		}),
		('Publishing', {
			'fields': ('display_order', 'is_published'),
		}),
	)

	@admin.display(description='Preview')
	def image_preview(self, obj):
		if obj.hero_image_upload:
			return format_html('<img src="{}" style="max-height:120px;border-radius:6px;">', obj.hero_image_upload.url)
		return '—'


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'created_at', 'ip_address')
	search_fields = ('name', 'email', 'message', 'ip_address')
	list_filter = ('created_at',)
	readonly_fields = ('name', 'email', 'message', 'ip_address', 'user_agent', 'created_at')


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
	form = ShopItemAdminForm
	list_display = ('title', 'catalog_category', 'category', 'icon', 'display_order', 'is_published', 'image_preview')
	list_editable = ('display_order', 'is_published')
	search_fields = ('title', 'catalog_category__name', 'category', 'description', 'icon')
	list_filter = ('is_published', 'catalog_category', 'category')
	readonly_fields = ('image_preview',)
	fieldsets = (
		('Content', {
			'fields': (
				'catalog_category',
				'title',
				'category',
				'icon',
				'image_upload',
				'remove_uploaded_image',
				'image_preview',
				'image_path',
				'link_url',
				'price_label',
				'cta_label',
				'description',
			),
			'description': 'Upload a shop image in admin. The legacy static path is optional fallback only.',
		}),
		('Publishing', {
			'fields': ('display_order', 'is_published'),
		}),
	)

	@admin.display(description='Preview')
	def image_preview(self, obj):
		if obj.image_upload:
			return format_html('<img src="{}" style="max-height:120px;border-radius:6px;">', obj.image_upload.url)
		if obj.image_path:
			return format_html('<img src="{}" style="max-height:120px;border-radius:6px;opacity:0.8;">', static(obj.image_path))
		return '—'


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug', 'display_order', 'is_published', 'item_total')
	list_editable = ('display_order', 'is_published')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name', 'description')
	list_filter = ('is_published',)
	readonly_fields = ('image_preview',)
	fieldsets = (
		('Category details', {
			'fields': ('name', 'slug', 'description', 'icon', 'image_upload', 'image_preview'),
			'description': 'This controls a public catalogue category. Add its items separately under Shop items.',
		}),
		('Publishing', {
			'fields': ('display_order', 'is_published'),
		}),
	)

	@admin.display(description='Items')
	def item_total(self, obj):
		return obj.items.count()

	@admin.display(description='Preview')
	def image_preview(self, obj):
		if obj.image_upload:
			return format_html('<img src="{}" style="max-height:120px;border-radius:6px;">', obj.image_upload.url)
		return '—'


@admin.register(ShopSectionSettings)
class ShopSectionSettingsAdmin(admin.ModelAdmin):
	fieldsets = (
		('Intro Copy', {
			'fields': ('eyebrow', 'heading', 'heading_highlight', 'description'),
		}),
		('CTA', {
			'fields': ('primary_cta_label', 'primary_cta_url', 'secondary_badge_label', 'secondary_badge_icon'),
		}),
	)

	def has_add_permission(self, request):
		return not ShopSectionSettings.objects.exists()


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
	list_display = ('visitor_fingerprint', 'visit_count', 'device_type', 'region', 'is_bot', 'first_seen', 'last_seen', 'last_path')
	search_fields = ('ip_hash', 'last_path', 'user_agent', 'region')
	list_filter = ('is_bot', 'device_type', 'first_seen', 'last_seen')
	readonly_fields = ('ip_hash', 'visit_count', 'device_type', 'region', 'is_bot', 'first_seen', 'last_seen', 'last_path', 'user_agent')
	ordering = ('-last_seen',)
	list_per_page = 50

	@admin.display(description='Anonymized IP')
	def visitor_fingerprint(self, obj):
		return obj.fingerprint

	def has_add_permission(self, request):
		return False


@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
	list_display = ('visitor_fingerprint', 'timestamp', 'path', 'is_bot')
	list_filter = ('is_bot', 'timestamp')
	search_fields = ('path', 'visitor__ip_hash')
	readonly_fields = ('visitor', 'timestamp', 'path', 'is_bot')
	ordering = ('-timestamp',)
	list_per_page = 50

	@admin.display(description='Visitor')
	def visitor_fingerprint(self, obj):
		return obj.visitor.fingerprint

	def has_add_permission(self, request):
		return False



@admin.register(PortfolioSettings)
class PortfolioSettingsAdmin(admin.ModelAdmin):
	fieldsets = (
		('Curriculum Vitae', {
			'fields': ('cv_file', 'cv_label'),
			'description': 'Upload the PDF shown by the CV button in the public desktop sidebar.',
		}),
	)
	readonly_fields = ('updated_at',)

	def has_add_permission(self, request):
		return not PortfolioSettings.objects.exists()


class ServiceInline(admin.StackedInline):
	model = Service
	extra = 0
	fieldsets = (
		(None, {
			'fields': (
				'title', 'slug', 'icon', 'short_description', 'description',
				'includes', 'outcomes', 'tags', 'column_span', 'show_bg_icon', 'display_order'
			),
		}),
	)


@admin.register(SiteContentSettings)
class SiteContentSettingsAdmin(admin.ModelAdmin):
	inlines = [ServiceInline]
	fieldsets = (
		('Hero Section', {
			'fields': ('hero_eyebrow', 'hero_description', 'hero_cta_label'),
		}),
		('Services Section', {
			'fields': ('services_eyebrow', 'services_heading', 'services_heading_highlight', 'services_intro'),
		}),
		('Featured Work Section', {
			'fields': ('work_eyebrow', 'work_heading', 'work_heading_highlight'),
		}),
		('Contact Section', {
			'fields': ('contact_eyebrow', 'contact_heading', 'contact_heading_highlight', 'contact_intro'),
		}),
		('Footer', {
			'fields': ('footer_text',),
		}),
	)

	def has_add_permission(self, request):
		return not SiteContentSettings.objects.exists()
