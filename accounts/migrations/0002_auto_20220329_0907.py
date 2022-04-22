# Generated by Django 3.2.5 on 2022-03-29 09:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('upload_clothes', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='email',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='like',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='phone',
        ),
        migrations.AddField(
            model_name='profile',
            name='myphoto',
            field=models.ImageField(blank=True, null=True, upload_to='images/myphoto/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='prefer_cloth',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='upload_clothes.cloth'),
        ),
    ]