# Generated by Django 2.2 on 2019-07-02 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sns', '0003_auto_20190629_0238'),
    ]

    operations = [
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sns.Message')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='share_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'share',
            },
        ),
    ]