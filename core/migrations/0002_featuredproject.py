from django.db import migrations, models


def seed_featured_projects(apps, schema_editor):
	FeaturedProject = apps.get_model('core', 'FeaturedProject')
	FeaturedProject.objects.update_or_create(
		slug='nexus-fintech',
		defaults={
			'title': 'Nexus Fintech',
			'category': 'Dashboard / Product Design',
			'card_summary': 'A calmer fintech operations dashboard concept with clearer hierarchy.',
			'headline': 'A sharper fintech operations dashboard built for trust, speed, and daily decision-making.',
			'summary': 'Nexus Fintech rethinks a cluttered internal dashboard into a calmer product surface with clearer hierarchy, faster reporting flows, and better conversion into meaningful operator actions.',
			'hero_image': 'img/work1.png',
			'challenge': 'The original product experience buried key metrics behind noisy widgets and forced operators to jump between disconnected views before they could make a decision.',
			'approach': 'I redesigned the information architecture around daily workflows, introduced modular reporting blocks, and tightened the visual system so important data surfaces faster.',
			'outcome': 'The result is a dashboard concept that feels executive-ready, reduces friction for repeat tasks, and gives the product a more premium, credible presence.',
			'services': 'UX strategy\nDashboard design\nDesign systems\nFrontend implementation',
			'stack': 'Django\nHTMX\nTailwind\nAnalytics UX',
			'display_order': 1,
			'is_published': True,
		},
	)
	FeaturedProject.objects.update_or_create(
		slug='velvet-estates',
		defaults={
			'title': 'Velvet Estates',
			'category': 'Luxury Landing Page',
			'card_summary': 'A premium real-estate landing page concept with stronger inquiry flow.',
			'headline': 'A real estate launch page designed to feel cinematic, premium, and conversion-ready.',
			'summary': 'Velvet Estates explores how a luxury property brand can present inventory, credibility, and inquiry capture through a more editorial, emotionally-led web experience.',
			'hero_image': 'img/work2.png',
			'challenge': 'The brief needed to balance aspiration with clarity: premium enough to sell exclusivity, but structured enough to guide a user toward booking a viewing.',
			'approach': 'I paired immersive imagery with tighter copy blocks, elevated spacing, and a cleaner inquiry path so the landing page could sell atmosphere without losing functional intent.',
			'outcome': 'The concept creates stronger first-impression impact, clearer offer framing, and a more deliberate path from browsing to high-intent contact.',
			'services': 'Creative direction\nLanding page design\nConversion UX\nFrontend build',
			'stack': 'Django\nResponsive UI\nGSAP\nContent design',
			'display_order': 2,
			'is_published': True,
		},
	)


def unseed_featured_projects(apps, schema_editor):
	FeaturedProject = apps.get_model('core', 'FeaturedProject')
	FeaturedProject.objects.filter(slug__in=['nexus-fintech', 'velvet-estates']).delete()


class Migration(migrations.Migration):

	dependencies = [
		('core', '0001_initial'),
	]

	operations = [
		migrations.CreateModel(
			name='FeaturedProject',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('title', models.CharField(max_length=200)),
				('slug', models.SlugField(unique=True)),
				('category', models.CharField(max_length=120)),
				('card_summary', models.CharField(max_length=200)),
				('headline', models.CharField(max_length=255)),
				('summary', models.TextField()),
				('hero_image', models.CharField(max_length=255)),
				('challenge', models.TextField()),
				('approach', models.TextField()),
				('outcome', models.TextField()),
				('services', models.TextField(help_text='One service per line.')),
				('stack', models.TextField(help_text='One stack item per line.')),
				('display_order', models.PositiveIntegerField(default=0)),
				('is_published', models.BooleanField(default=True)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
			],
			options={
				'ordering': ['display_order', 'title'],
			},
		),
		migrations.RunPython(seed_featured_projects, unseed_featured_projects),
	]