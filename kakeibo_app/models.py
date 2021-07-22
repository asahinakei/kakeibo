from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
COST  = [(1, '水道'), (2, '電気'), (3, 'ガス'), (4, '家賃'), (5, '通信費'), (6, '食費'), (7, '趣味'), (8, 'サブスク'), (9, 'その他')]
YEAR  = [(2020, '2020年'), (2021, '2021年'), (2022, '2022年'), (2023, '2023年'), (2024, '2024年'), (2025, '2025年')]
MONTH = [(1, '1月'), (2, '2月'), (3, '3月'), (4, '4月'), (5, '5月'), (6, '6月'), (7, '7月'), (8, '8月'), (9, '9月'), (10, '10月'), (11, '11月'), (12, '12月')]

class Kakeibo(models.Model):
    # 基本情報用
    class Meta:
        verbose_name = '家計簿'
        verbose_name_plural = '家計簿'
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cost = models.PositiveSmallIntegerField(verbose_name='支出項目', choices=COST)
    year = models.PositiveSmallIntegerField(verbose_name='年', choices=YEAR)
    month = models.PositiveSmallIntegerField(verbose_name='月', choices=MONTH)
    money = models.IntegerField(verbose_name='金額')
    memo = models.TextField(verbose_name='メモ', blank=True, null=True, max_length=50)
    code = models.CharField(max_length=50, blank=True, unique=True)
    date = models.DateTimeField(auto_now=True)
    def __str__(self):
        index = Kakeibo(self)
        return (
            str(self.owner) + ':'
            + str(self.year) + '年'
            + str(self.month) + '月'
            + str(self.cost)
        )