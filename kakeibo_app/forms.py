from django.forms import Textarea
from django import forms
from .models import Kakeibo

COST  = [('', '選択してください'), (1, '水道'), (2, '電気'), (3, 'ガス'), (4, '家賃'), (5, '通信費'), (6, '食費'), (7, '趣味'), (8, 'サブスク'), (9, 'その他')]
YEAR  = [('', '選択してください'), (2021, '2021年'), (2022, '2022年'), (2023, '2023年'), (2024, '2024年'), (2025, '2025年'), (2026, '2026年')]
MONTH = [('', '選択してください'), (1, '1月'), (2, '2月'), (3, '3月'), (4, '4月'), (5, '5月'), (6, '6月'), (7, '7月'), (8, '8月'), (9, '9月'), (10, '10月'), (11, '11月'), (12, '12月')]
    
class KakeiboForm(forms.Form):
    cost = forms.ChoiceField(label='支出項目', choices=COST)
    year = forms.ChoiceField(label='年', choices=YEAR)
    month = forms.ChoiceField(label='月', choices=MONTH, widget=forms.Select(attrs={'placeholder': '選択'}))
    money = forms.IntegerField(label='金額', help_text=' 円', widget=forms.NumberInput(
            attrs={'placeholder':'半角入力'}))
    memo = forms.CharField(
        label='メモ',
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder':'コメント',
            }
        )
    )


# まとめて入力        
class MultiEntryForm(forms.Form):
    cost = forms.ChoiceField(label='支出項目', choices=COST)
    year_1 = forms.ChoiceField(label='年', choices=YEAR)
    year_2 = forms.ChoiceField(label='年', choices=YEAR)
    month_1 = forms.ChoiceField(label='月', choices=MONTH)
    month_2 = forms.ChoiceField(label='月', choices=MONTH)
    money = forms.IntegerField(label='金額', help_text=' 円', widget=forms.TextInput(
            attrs={'placeholder':'半角入力'}))
    memo = forms.CharField(
        label='メモ',
        required=False,
        widget=forms.Textarea(attrs={'placeholder':'コメント'})
    )
# まとめて入力から削除へデータ渡す用
class DeleteDataForm(forms.Form):
    code = forms.CharField()

# 編集
class EditStartForm(forms.Form):
    cost = forms.ChoiceField(label='支出項目', choices=COST)
    year = forms.ChoiceField(label='年', choices=YEAR)
    month = forms.ChoiceField(label='月', choices=MONTH)
# 編集
class EditForm(forms.Form):
    money = forms.IntegerField(
        label='金額',
        help_text=' 円',
        widget=forms.TextInput(attrs={'placeholder':'半角入力'})
        )
    memo = forms.CharField(
        label='メモ',
        required=False,
        widget=forms.Textarea(
            attrs={'placeholder':'コメント'})
        )

# 削除
class DeleteForm(forms.Form):
    cost = forms.ChoiceField(label='支出項目', choices=COST)
    year = forms.ChoiceField(label='年', choices=YEAR)
    month = forms.ChoiceField(label='月', choices=MONTH)

# まとめて削除        
class MultiDeleteForm(forms.Form):
    cost = forms.ChoiceField(label='支出項目', choices=COST)
    year_1 = forms.ChoiceField(label='年', choices=YEAR)
    year_2 = forms.ChoiceField(label='年', choices=YEAR)
    month_1 = forms.ChoiceField(label='月', choices=MONTH)
    month_2 = forms.ChoiceField(label='月', choices=MONTH)

# テーブル
class TableForm(forms.Form):
    year = forms.ChoiceField(label='年', choices=YEAR)

# グラフ
class GraphForm(forms.Form):
    cost = forms.ChoiceField(label='支出項目', choices=COST)
    year = forms.ChoiceField(label='年', choices=YEAR)
   
# 比較
class ChoiceYearForm(forms.Form):
    YEARS = [('', '選択してください'), (2, '2年分'), (3, '3年分'), (4, '4年分'), (5, '5年分'), (6, '6年分') ]
    cost = forms.ChoiceField(label='支出項目', choices=COST)
    how_many_years = forms.ChoiceField(label='比較年数', choices=YEARS, required=True)
# 比較
class ComparisonForm(forms.Form):
    year_1 = forms.ChoiceField(label='年', choices=YEAR, required=False)
    year_2 = forms.ChoiceField(label='年', choices=YEAR, required=False)
    year_3 = forms.ChoiceField(label='年', choices=YEAR, required=False)
    year_4 = forms.ChoiceField(label='年', choices=YEAR, required=False)
    year_5 = forms.ChoiceField(label='年', choices=YEAR, required=False)
    year_6 = forms.ChoiceField(label='年', choices=YEAR, required=False)
