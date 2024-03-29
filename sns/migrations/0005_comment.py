# Generated by Django 2.2 on 2019-07-03 04:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sns', '0004_share'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply', models.TextField(max_length=150, verbose_name='reply_content')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='reply_date')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sns.Message', verbose_name='message_connected')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reply_owner', to=settings.AUTH_USER_MODEL, verbose_name='reply_owner')),
            ],
            options={
                'db_table': 'comment',
            },
        ),
    ]
