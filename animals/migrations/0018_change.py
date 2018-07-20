# Generated by Django 2.0.6 on 2018-06-21 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0017_auto_20180621_0943'),
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('new', 'new'), ('adaption', 'adaption'), ('deletion', 'deletion')], default='adaption', max_length=100)),
                ('version', models.CharField(max_length=200)),
                ('short_text', models.CharField(max_length=400)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(upload_to='images/')),
            ],
        ),
    ]