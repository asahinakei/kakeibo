# Generated by Django 3.2.5 on 2021-07-13 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo_app', '0004_auto_20210711_1746'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kakeibo',
            old_name='value',
            new_name='money',
        ),
        migrations.AlterField(
            model_name='kakeibo',
            name='cost',
            field=models.PositiveSmallIntegerField(choices=[(1, '水道'), (2, '電気'), (3, 'ガス'), (4, '家賃'), (5, '通信費'), (6, '食費'), (7, '趣味'), (8, 'サブスク'), (9, 'その他')], verbose_name='支出項目'),
        ),
        migrations.DeleteModel(
            name='Item',
        ),
    ]