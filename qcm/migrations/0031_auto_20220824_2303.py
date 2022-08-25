# Generated by Django 3.0.5 on 2022-08-24 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qcm', '0030_auto_20220729_0936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='supportfile',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='qcm.Supportfile', verbose_name='Fichier Géogebra'),
        ),
        migrations.AlterField(
            model_name='mastering',
            name='exercise',
            field=models.ForeignKey(blank=True, default='', editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exercise', to='qcm.Exercise'),
        ),
        migrations.AlterField(
            model_name='mastering',
            name='relationship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relationship_mastering', to='qcm.Relationship', verbose_name='Exercice'),
        ),
        migrations.AlterField(
            model_name='mastering_done',
            name='mastering',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='mastering_done', to='qcm.Mastering', verbose_name='Exercice'),
        ),
        migrations.AlterField(
            model_name='masteringcustom_done',
            name='mastering',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='mastering_custom_done', to='qcm.Masteringcustom', verbose_name='Exercice'),
        ),
    ]