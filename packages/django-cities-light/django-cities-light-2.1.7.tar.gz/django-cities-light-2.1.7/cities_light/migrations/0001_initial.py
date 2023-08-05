# encoding: utf8
from django.db import models, migrations
import autoslug.fields
import cities_light.models


class Migration(migrations.Migration):
    
    dependencies = []

    operations = [
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('name_ascii', models.CharField(db_index=True, max_length=200, blank=True),), ('slug', autoslug.fields.AutoSlugField(editable=False),), ('geoname_id', models.IntegerField(unique=True, null=True, blank=True),), ('alternate_names', models.TextField(default='', null=True, blank=True),), ('name', models.CharField(unique=True, max_length=200),), ('code2', models.CharField(max_length=2, unique=True, null=True, blank=True),), ('code3', models.CharField(max_length=3, unique=True, null=True, blank=True),), ('continent', models.CharField(db_index=True, max_length=2, choices=(('OC', u'Oceania',), ('EU', u'Europe',), ('AF', u'Africa',), ('NA', u'North America',), ('AN', u'Antarctica',), ('SA', u'South America',), ('AS', u'Asia',),)),), ('tld', models.CharField(db_index=True, max_length=5, blank=True),)],
            bases = (models.Model,),
            options = {u'ordering': ['name'], u'abstract': False, u'verbose_name_plural': u'countries'},
            name = 'Country',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('name_ascii', models.CharField(db_index=True, max_length=200, blank=True),), ('slug', autoslug.fields.AutoSlugField(editable=False),), ('geoname_id', models.IntegerField(unique=True, null=True, blank=True),), ('alternate_names', models.TextField(default='', null=True, blank=True),), ('name', models.CharField(max_length=200, db_index=True),), ('display_name', models.CharField(max_length=200),), ('geoname_code', models.CharField(db_index=True, max_length=50, null=True, blank=True),), ('country', models.ForeignKey(to=u'cities_light.Country', to_field=u'id'),)],
            bases = (models.Model,),
            options = {u'ordering': ['name'], u'unique_together': set([('country', 'name',)]), u'abstract': False, u'verbose_name': u'region/state', u'verbose_name_plural': u'regions/states'},
            name = 'Region',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('name_ascii', models.CharField(db_index=True, max_length=200, blank=True),), ('slug', autoslug.fields.AutoSlugField(editable=False),), ('geoname_id', models.IntegerField(unique=True, null=True, blank=True),), ('alternate_names', models.TextField(default='', null=True, blank=True),), ('name', models.CharField(max_length=200, db_index=True),), ('display_name', models.CharField(max_length=200),), ('search_names', cities_light.models.ToSearchTextField(default='', max_length=4000, db_index=True, blank=True),), ('latitude', models.DecimalField(null=True, max_digits=8, decimal_places=5, blank=True),), ('longitude', models.DecimalField(null=True, max_digits=8, decimal_places=5, blank=True),), ('region', models.ForeignKey(to_field=u'id', blank=True, to=u'cities_light.Region', null=True),), ('country', models.ForeignKey(to=u'cities_light.Country', to_field=u'id'),), ('population', models.BigIntegerField(db_index=True, null=True, blank=True),), ('feature_code', models.CharField(db_index=True, max_length=10, null=True, blank=True),)],
            bases = (models.Model,),
            options = {u'ordering': ['name'], u'unique_together': set([('region', 'name',)]), u'abstract': False, u'verbose_name_plural': u'cities'},
            name = 'City',
        ),
    ]
