# Generated by Django 3.0.5 on 2021-06-23 18:28

import association.models
import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('school', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Accounting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, editable=False, max_digits=10)),
                ('is_credit', models.BooleanField(default=0)),
                ('objet', models.CharField(max_length=255, verbose_name='Objet*')),
                ('chrono', models.CharField(blank=True, editable=False, max_length=50, unique=True)),
                ('mode', models.CharField(blank=True, choices=[('par carte de crédit', 'Carte de crédit'), ('par virement bancaire', 'Virement bancaire'), ('en espèces', 'Espèces'), ('par mandatement administratif', 'Mandatement administratif')], default='', max_length=255, verbose_name='Mode de paiement')),
                ('forme', models.CharField(blank=True, choices=[('FACTURE', 'FACTURE'), ('AVOIR', 'AVOIR'), ('DEVIS', 'DEVIS'), ('REMBOURSEMENT', 'REMBOURSEMENT')], default='FACTURE', max_length=255, verbose_name='Format')),
                ('beneficiaire', models.CharField(blank=True, max_length=255, verbose_name='En faveur de')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='Adresse')),
                ('complement', models.CharField(blank=True, max_length=255, verbose_name="Complément d'adresse")),
                ('town', models.CharField(blank=True, max_length=255, verbose_name="Complément d'adresse")),
                ('contact', models.CharField(blank=True, max_length=255, verbose_name='Contact')),
                ('observation', ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='', null=True, verbose_name='Observation')),
                ('acting', models.DateTimeField(blank=True, null=True, verbose_name="Date d'effet")),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=0, verbose_name='Actif')),
                ('is_abonnement', models.BooleanField(default=0, verbose_name='Abonnement')),
                ('ticket', models.FileField(blank=True, default='', upload_to=association.models.accounting_directory_path, verbose_name='Justificatif')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='accontings', to='school.Country', verbose_name='Pays')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accontings', to='school.School', verbose_name='Etablissement')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='accontings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Associate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quality', models.CharField(choices=[('actif', 'membre actif'), ('honneur', "membre d'honneur"), ('bienfaiteur', 'membre bienfaiteur'), ('bénéficiaire', 'membre bénéficiaire')], default='', max_length=255, verbose_name='Qualité')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=0, editable=False)),
                ('first_name', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Nom')),
                ('last_name', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Prénom')),
                ('email', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Email')),
                ('observation', ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='', null=True, verbose_name='Remarque')),
                ('user', models.ForeignKey(blank=True, default=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='associated', to=settings.AUTH_USER_MODEL, verbose_name='Membre inscrit')),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Tarif')),
                ('discount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Réduction')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name="Nombre d'élèves")),
                ('year', models.CharField(default='', max_length=255, verbose_name='Année')),
                ('is_active', models.BooleanField(default=0, verbose_name='Année active')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=255, verbose_name='Titre')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', max_length=255, verbose_name='Titre')),
                ('annoncement', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='Texte*')),
                ('ranking', models.PositiveIntegerField(blank=True, default=0, editable=False, null=True, verbose_name='Ordre')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Date de modification')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='association.Section', verbose_name='Section')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Detail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Description')),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10)),
                ('accounting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='association.Accounting', verbose_name='Pays')),
            ],
        ),
        migrations.CreateModel(
            name='Abonnement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateTimeField(blank=True, verbose_name='Date de début')),
                ('date_stop', models.DateTimeField(blank=True, verbose_name='Date de fin')),
                ('is_gar', models.BooleanField(default=0, verbose_name='Usage du GAR')),
                ('is_active', models.BooleanField(default=0, verbose_name='Actif')),
                ('accounting', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='abonnement', to='association.Accounting')),
                ('school', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='abonnement', to='school.School')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='abonnement', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Voting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.BooleanField(default=0, verbose_name='vote')),
                ('justification', models.CharField(blank=True, default='', max_length=255, verbose_name='justification (facultatif)')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('associate', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='voting', to='association.Associate')),
                ('user', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='votant', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('associate', 'user')},
            },
        ),
    ]
