from django.contrib import admin

from .models import ContactSubmission, FeaturedProject, ShopItem, ShopSectionSettings


admin.site.site_header = 'Muko Admin'
admin.site.site_title = 'Muko Admin'
admin.site.index_title = 'Content Control Center'


@admin.register(FeaturedProject)
class FeaturedProjectAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'filter_group', 'display_order', 'is_published')
	list_editable = ('filter_group', 'display_order', 'is_published')
	prepopulated_fields = {'slug': ('title',)}
	search_fields = ('title', 'category', 'headline', 'summary')
	list_filter = ('is_published', 'filter_group')
	fieldsets = (
		('Card Content', {
			'fields': ('title', 'slug', 'category', 'filter_group', 'card_summary', 'hero_image'),
		}),
		('Detail Page Content', {
			'fields': ('headline', 'summary', 'challenge', 'approach', 'outcome', 'services', 'stack'),
		}),
		('Publishing', {
			'fields': ('display_order', 'is_published'),
		}),
	)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'created_at', 'ip_address')
	search_fields = ('name', 'email', 'message', 'ip_address')
	list_filter = ('created_at',)
	readonly_fields = ('name', 'email', 'message', 'ip_address', 'user_agent', 'created_at')


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'icon', 'display_order', 'is_published')
	list_editable = ('display_order', 'is_published')
	search_fields = ('title', 'category', 'description', 'icon')
	list_filter = ('is_published', 'category')
	fieldsets = (
		('Content', {
			'fields': ('title', 'category', 'icon', 'image_path', 'link_url', 'description'),
		}),
		('Publishing', {
			'fields': ('display_order', 'is_published'),
		}),
	)


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
