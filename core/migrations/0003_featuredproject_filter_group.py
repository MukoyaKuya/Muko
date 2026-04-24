from django.db import migrations, models


def seed_filter_groups(apps, schema_editor):
	FeaturedProject = apps.get_model('core', 'FeaturedProject')
	FeaturedProject.objects.filter(slug='nexus-fintech').update(filter_group='web')
	FeaturedProject.objects.filter(slug='velvet-estates').update(filter_group='design')


class Migration(migrations.Migration):

	dependencies = [
		('core', '0002_featuredproject'),
	]

	operations = [
		migrations.AddField(
			model_name='featuredproject',
			name='filter_group',
			field=models.CharField(
				choices=[('web', 'Web'), ('design', 'Design')],
				default='web',
				help_text='Controls which homepage filter chip shows this project.',
				max_length=20,
			),
		),
		migrations.AlterField(
			model_name='featuredproject',
			name='hero_image',
			field=models.CharField(help_text='Path relative to static/, for example img/work1.png', max_length=255),
		),
		migrations.AlterField(
			model_name='featuredproject',
			name='services',
			field=models.TextField(help_text='One service per line, in the order you want them displayed.'),
		),
		migrations.AlterField(
			model_name='featuredproject',
			name='stack',
			field=models.TextField(help_text='One stack item per line, for the chips on the detail page.'),
		),
		migrations.RunPython(seed_filter_groups, migrations.RunPython.noop),
	]