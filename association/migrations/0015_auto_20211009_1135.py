# Generated by Django 3.0.5 on 2021-10-09 10:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0005_auto_20210904_1909'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('association', '0014_auto_20210916_1115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounting',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accountings', to='school.Country', verbose_name='Pays'),
        ),
        migrations.AlterField(
            model_name='accounting',
            name='plan',
            field=models.ForeignKey(blank=True, default=17, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plan_accountings', to='association.Plancomptable', verbose_name='Plan comptable'),
        ),
        migrations.AlterField(
            model_name='accounting',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountings', to='school.School', verbose_name='Etablissement'),
        ),
        migrations.AlterField(
            model_name='accounting',
            name='user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accountings', to=settings.AUTH_USER_MODEL),
        ),
    ]
