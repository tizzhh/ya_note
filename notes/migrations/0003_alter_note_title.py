# Generated by Django 3.2.15 on 2023-12-18 10:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('notes', '0002_alter_note_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(
                default='Название заметки',
                help_text='Дайте короткое название заметке',
                max_length=100,
                verbose_name='Заголовок',
            ),
        ),
    ]
