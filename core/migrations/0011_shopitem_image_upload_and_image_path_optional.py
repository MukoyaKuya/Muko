from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('core', '0010_update_shopsectionsettings_heading_default'),
	]

	operations = [
		migrations.AddField(
			model_name='shopitem',
			name='image_upload',
			field=models.ImageField(blank=True, help_text='Upload a shop image. This is used first when present.', null=True, upload_to='shop/'),
		),
		migrations.AlterField(
			model_name='shopitem',
			name='image_path',
			field=models.CharField(blank=True, help_text='Optional legacy path relative to static/, for example img/work3.png.', max_length=255),
		),
	]
