from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('recommender', '0002_jarakcache')]
    operations = [
        migrations.AddField('destination', 'source_id', models.PositiveIntegerField(blank=True, null=True, unique=True)),
        migrations.AlterField('destination', 'rating', models.FloatField(blank=True, null=True)),
        migrations.AddField('destination', 'rating_model', models.FloatField(blank=True, null=True)),
        migrations.AddField('destination', 'rating_imputed', models.BooleanField(default=False)),
        migrations.AddField('destination', 'description', models.TextField(blank=True, default='')),
        migrations.AddField('destination', 'provenance', models.JSONField(blank=True, default=dict)),
        migrations.AddField('destination', 'data_quality', models.JSONField(blank=True, default=dict)),
        migrations.AddField('destination', 'pipeline_fingerprint', models.CharField(blank=True, default='', max_length=64)),
        migrations.AddField('destination', 'fas_accessibility', models.BooleanField(default=False)),
        migrations.AddField('destination', 'fas_information_center', models.BooleanField(default=False)),
    ]
