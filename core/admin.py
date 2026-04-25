from django import forms
from django.contrib import admin
from django.templatetags.static import static
from django.utils.html import format_html

from .models import ContactSubmission, FeaturedProject, ProjectImage, ShopItem, ShopSectionSettings


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
	extra = 3
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
	readonly_fields = ('image_preview',)
	inlines = [ProjectImageInline]
	fieldsets = (
		('Card Content', {
			'fields': ('title', 'slug', 'category', 'filter_group', 'card_summary', 'live_url'),
		}),
		('Hero Image', {
			'fields': ('hero_image_upload', 'remove_uploaded_hero_image', 'image_preview', 'hero_image'),
			'description': 'Upload a screenshot or hero image. The uploaded file takes priority; the legacy path is a fallback for existing projects.',
		}),
		('Detail Page Content', {
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
	list_display = ('title', 'category', 'icon', 'display_order', 'is_published', 'image_preview')
	list_editable = ('display_order', 'is_published')
	search_fields = ('title', 'category', 'description', 'icon')
	list_filter = ('is_published', 'category')
	readonly_fields = ('image_preview',)
	fieldsets = (
		('Content', {
			'fields': (
				'title',
				'category',
				'icon',
				'image_upload',
				'remove_uploaded_image',
				'image_preview',
				'image_path',
				'link_url',
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
