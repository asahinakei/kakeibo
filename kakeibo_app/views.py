from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import Error, IntegrityError
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

from .forms import KakeiboForm
from .forms import MultiEntryForm
from .forms import DeleteDataForm
from .forms import EditForm
from .forms import EditStartForm
from .forms import TableForm
from .forms import GraphForm
from .forms import ComparisonForm
from .forms import ChoiceYearForm
from .forms import DeleteForm
from .forms import MultiDeleteForm

from .models import Kakeibo

COST = {
    1: '水道',
    2: '電気',
    3: 'ガス',
    4: '家賃',
    5: '通信費',
    6: '食費',
    7: '趣味',
    8: 'サブスク',
    9: 'その他',
}



# Create your views here.
def index(request):
# ホーム画面
    return render(request, 'index.html')

@login_required
# 入力
def entry(request):
    if request.method == 'POST':
        form = KakeiboForm(request.POST)
        if form.is_valid():
            try:
                cost = form.cleaned_data['cost']
                year = form.cleaned_data['year']
                month = form.cleaned_data['month']
                money = form.cleaned_data['money']
                memo = form.cleaned_data['memo']
                code = str(request.user) \
                    + str(year) \
                    + '-' \
                    + str(month) \
                    + '-' \
                    + str(cost)
                Kakeibo.objects.create(
                    cost = cost,
                    year = year,
                    month = month,
                    money = money,
                    memo = memo,
                    code = code,
                    owner = request.user,
                    )
                qs = Kakeibo.objects.get(code=code)
                context = {'qs': qs}
                return render(request, 'entry_success.html', context)
            except IntegrityError:
                frag = True
                cost = COST[int(form.cleaned_data['cost'])]
                context = {
                    'form': form,
                    'frag': frag,
                    'cost': cost,
                    }
                return render(request, 'entry.html', context)
    else:
        form = KakeiboForm()
    context = {'form': form}
    return render(request, 'entry.html', context)

@login_required
def edit_start_from_entry(request):
# 編集
# 入力が登録済みエラーとなり、編集リンクへ遷移した場合
    start_form = EditStartForm(request.POST)
    form = EditForm()
    from_entry_frag = True
    code = str(request.user) \
        + str(request.POST['year']) \
        + '-' \
        + str(request.POST['month']) \
        + '-' \
        + str(request.POST['cost'])
    qs = Kakeibo.objects.get(code=code)
    context ={
        'start_form': start_form,
        'form': form,
        'qs': qs,
        'from_entry_frag': from_entry_frag,
        }
    return render(request, 'edit.html', context)

@login_required
def edit_from_entry(request):
# 編集　edit_start_from_entry の続き
# 既存のデータベースの金額とメモだけ変更して保存する
    start_form = EditStartForm(request.POST)
    form = EditForm(request.POST)
    if start_form.is_valid() and form.is_valid():
        code = str(request.user) \
            + str(start_form.cleaned_data['year']) \
            + '-' \
            + str(start_form.cleaned_data['month']) \
            + '-' \
            + str(start_form.cleaned_data['cost'])
        qs = Kakeibo.objects.get(code=code)
        new_money = form.cleaned_data['money']
        new_memo = form.cleaned_data['memo']
        if qs.money == new_money and qs.memo == new_memo:
            from_entry_frag = True
            no_change_frag = True
            context = {
                'start_form': start_form,
                'form': form,
                'from_entry_frag': from_entry_frag,
                'no_change_frag': no_change_frag,
                'qs': qs,
                }
            return render(request, 'edit.html', context)
        else:
            qs.money = new_money
            qs.memo = new_memo
            qs.save()
            context = {'qs': qs}
            return render(request, 'edit_success.html', context)

@login_required
def multi_entry(request):
# まとめて入力
    if request.method == 'POST':
        form = MultiEntryForm(request.POST)
        if form.is_valid():
            cost = form.cleaned_data['cost'] 
            year_1 = int(form.cleaned_data['year_1'])
            year_2 = int(form.cleaned_data['year_2'])
            month_1 = int(form.cleaned_data['month_1'])
            month_2 = int(form.cleaned_data['month_2'])
            money = form.cleaned_data['money']              
            memo = form.cleaned_data['memo']
            # data_list : 登録済みエラー用
            data_list = []
            year_month_frag = False
            if year_1 > year_2:
                year_month_frag = True
            elif year_1 == year_2:
                if month_1 >= month_2:
                    year_month_frag = True
                else:
                    i = month_1     
                    try:
                        while int(i) <= month_2:
                            year = year_1
                            code = str(request.user) \
                                + str(year) \
                                + '-' \
                                + str(i) \
                                + '-' \
                                + str(cost)
                            data = Kakeibo.objects.create(
                                year=year,
                                month=i,
                                cost=cost,
                                money=money,
                                code=code,
                                memo=memo,
                                owner=request.user,
                                )
                            data_list.append(data)
                            i = int(i)+ 1
                        cost = COST[int(cost)]
                        context = {
                            'cost': cost,
                            'form': form,
                            }
                        return render(request, 'multi_entry_success.html', context)
                    except IntegrityError:
                        duplicate_frag = True
                        for data in data_list:
                            del_data = Kakeibo.objects.get(code=data.code)
                            del_data.delete()
                        qs = Kakeibo.objects.get(code=code)
                        del_data_form = DeleteDataForm({'code': code})
                        context = {
                            'form': form,
                            'year_1': year_1,
                            'year_2': year_2,
                            'month_1': month_1,
                            'month_2': month_2,
                            'duplicate_frag': duplicate_frag,
                            'qs': qs,
                            'del_data_form': del_data_form,
                            }
                        return render(request, 'multi_entry.html', context)
            elif year_1 < year_2:
                i = year_1
                j = month_1 
                try:
                    while int(i) < year_2:
                        while int(j) <= 12:
                            code = str(request.user) \
                                + str(i) \
                                + '-' \
                                + str(j) \
                                + '-' \
                                +str(cost)
                            data = Kakeibo.objects.create(
                                year=i,
                                month=j,
                                cost=cost,
                                money=money,
                                code=code,
                                memo=memo,
                                owner=request.user,
                                )
                            data_list.append(data)
                            j = int(j)+ 1
                        j = 1
                        i = int(i) + 1
                    while j <= month_2:
                        code = str(request.user) \
                            + str(i) \
                            + '-' \
                            + str(j) \
                            + '-' \
                            + str(cost)
                        data = Kakeibo.objects.create(
                            year=i,
                            month=j,
                            cost=cost,
                            money=money,
                            code=code,
                            memo=memo,
                            owner=request.user,
                            )
                        data_list.append(data)
                        j = int(j) + 1
                    cost = COST[int(cost)]
                    context = {
                        'cost': cost,
                        'form': form,
                        }
                    return render(request, 'multi_entry_success.html', context)
                except IntegrityError:
                    duplicate_frag = True
                    # まとめて入力が途中で登録済みエラーを起こしたので、すでに入力したデータdata_listを削除する
                    for data in data_list:
                        data = Kakeibo.objects.get(code=data.code)
                        data.delete()
                    qs = Kakeibo.objects.get(code=code)
                    del_data_form = DeleteDataForm({'code': code})
                    context = {
                        'form': form,
                        'year_1': year_1,
                        'year_2': year_2,
                        'month_1': month_1,
                        'month_2': month_2,
                        'duplicate_frag': duplicate_frag,
                        'qs': qs,
                        'del_data_form': del_data_form,
                        }
                    return render(request, 'multi_entry.html', context)
            context = {
                'form': form,
                'year_1': year_1,
                'year_2': year_2,
                'month_1': month_1,
                'month_2': month_2,
                'year_month_frag': year_month_frag,
            }
            return render(request, 'multi_entry.html', context)
    else:
        form = MultiEntryForm()
    context = {'form': form}
    return render(request, 'multi_entry.html', context)

@login_required                
def del_start_from_multi_entry(request):
# まとめて入力が登録済みエラーになって、削除画面へのリンクがクリックされた場合
    code = request.POST['code']
    qs = Kakeibo.objects.get(code=code)
    data = {
        'cost': qs.cost,
        'year': qs.year,
        'month': qs.month,
        }
    form = DeleteForm(data)
    context = {
        'form': form,
        'qs': qs,
    }
    return render(request, 'delete.html', context)
        
@login_required                
def del_from_multi_entry(request):
# 削除 del_start_from_multi_entryの続き
    del_data_form = DeleteDataForm(request.POST)
    code = request.POST['code']
    qs = Kakeibo.objects.get(code=code)
    year = qs.year
    month = qs.month
    money = qs.money
    memo =  qs.memo
    cost = COST[int(qs.cost)]
    qs.delete()
    context = {
        'cost': cost,
        'year': year,
        'month': month,
        'money': money,
        'memo': memo,
        }
    return render(request, 'delete_success.html', context)
    
@login_required
def edit_start(request):
# 編集
# どのデータを編集するのか選択させてeditへ送る
# start_formはデータ送信のために隠してeditへ送る
    if request.method == 'POST':
        start_form = EditStartForm(request.POST)
        form = EditForm()
        if start_form.is_valid():
            try:
                year = start_form.cleaned_data['year']
                month = start_form.cleaned_data['month']
                cost = start_form.cleaned_data['cost']
                code = str(request.user) \
                    + str(year) \
                    + '-' \
                    + str(month) \
                    + '-' \
                    + str(cost)
                qs = Kakeibo.objects.get(code=code)
                context = {
                    'start_form': start_form,
                    'form': form,
                    'qs': qs,
                    }
                return render(request, 'edit.html', context)
            except ObjectDoesNotExist:
                no_exist_frag = True
                to_entry_frag = True
                data = {
                    'year': year,
                    'month': month,
                    'cost': cost,
                    }
                # 入力画面へのリンクがクリックされたら、dataの情報をentry_fromに格納してentryビューへ渡す
                entry_form = KakeiboForm(data)
                cost = COST[int(cost)]
                context = {
                    'start_form': start_form,
                    'no_exist_frag': no_exist_frag,
                    'to_entry_frag': to_entry_frag,
                    'cost': cost,
                    'entry_form': entry_form,
                }
                return render(request, 'edit_start.html', context)    
    else:
        start_form = EditStartForm()
    context = {'start_form': start_form}
    return render(request, 'edit_start.html', context)

@login_required
def edit(request):
# 編集　edit_startの続き
# 既存のデータの金額とメモだけ変更して保存する
    start_form = EditStartForm(request.POST)
    form = EditForm(request.POST)
    if form.is_valid():
        code = str(request.user) \
            + str(request.POST['year']) \
            + '-' \
            + str(request.POST['month']) \
            + '-' \
            + str(request.POST['cost'])
        qs = Kakeibo.objects.get(code=code)
        new_money = form.cleaned_data['money']
        new_memo = form.cleaned_data['memo']
        if qs.money == new_money and qs.memo == new_memo:
            no_change_frag = True
            context = {
                'start_form': start_form,
                'form': form,
                'qs': qs,
                'no_change_frag': no_change_frag,
            }
            return render(request, 'edit.html', context)
        else:
            qs.money = new_money
            qs.memo = new_memo
            qs.save()
            context = {'qs': qs}
            return render(request, 'edit_success.html', context)

        

@login_required                
def delete_start(request):
# 削除
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            cost = form.cleaned_data['cost']
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            try:
                code = str(request.user) \
                    + year \
                    + '-' \
                    + month \
                    + '-' \
                    + cost
                qs = Kakeibo.objects.get(code=code)
                context = {
                    'form': form,
                    'qs': qs,
                }
                return render(request, 'delete.html', context)
            except ObjectDoesNotExist:
                no_exist_frag = True
                data = {
                    'year': year,
                    'month': month,
                    'cost': cost,
                }
                cost = COST[int(cost)]
                entry_form = KakeiboForm(data)
                context = {
                    'form': form,
                    'cost': cost,
                    'year': year,
                    'month': month,
                    'no_exist_frag': no_exist_frag,
                    'entry_form': entry_form,
                }
                return render(request, 'delete_start.html', context)
    else:
        form = DeleteForm()     
    context = {'form': form}
    return render(request, 'delete_start.html', context)

@login_required            
def delete(request):
# 削除　delete_startの続き
    form = DeleteForm(request.POST)        
    year = request.POST['year']
    month = request.POST['month']
    cost = COST[int(request.POST['cost'])]
    code = str(request.user) \
        + year \
        + '-' \
        + month \
        + '-' \
        + str(request.POST['cost'])
    qs = Kakeibo.objects.get(code=code)
    money = qs.money
    memo = qs.memo
    qs.delete()
    context = {
            'year': year,
            'month': month,
            'cost': cost,
            'money': money,
            'memo': memo,
        }
    return render(request, 'delete_success.html', context)

@login_required
def multi_delete_start(request):
    # まとめて削除
    if request.method == 'POST':
        form = MultiDeleteForm(request.POST)
        if form.is_valid():
            cost = form.cleaned_data['cost']
            year_1 = int(form.cleaned_data['year_1'])
            year_2 = int(form.cleaned_data['year_2'])
            month_1 = int(form.cleaned_data['month_1'])
            month_2 = int(form.cleaned_data['month_2'])
            i = year_1
            j = month_1
            # データが存在するかチェックする
            if year_1 > year_2:
                year_month_frag = True
            elif year_1 == year_2:
                if month_1 >= month_2:
                    year_month_frag = True
                else:
                    try:
                        while j <= month_2:
                            code = str(request.user) \
                                + str(year_1) \
                                + '-' \
                                + str(j) \
                                + '-' \
                                + str(cost)
                            qs = Kakeibo.objects.get(code=code)
                            j += 1
                        cost = COST[int(cost)]
                        context = {
                            'form': form,
                            'cost': cost,
                            }
                        return render(request, 'multi_delete.html', context)
                    except ObjectDoesNotExist:
                        no_exist_frag = True
                        data = {
                            'year': i,
                            'month': j,
                            'cost': cost,
                            }
                        entry_form = KakeiboForm(data)
                        cost = COST[int(cost)]
                        context = {
                            'form': form,
                            'i': i,
                            'j': j,
                            'cost': cost,
                            'no_exist_frag': no_exist_frag,
                            'entry_form': entry_form,
                            }
                        return render(request, 'multi_delete_start.html', context)
            elif year_1 < year_2:
                try:
                    while i < year_2:
                        while j <= 12:
                            code = str(request.user) \
                                + str(i) \
                                + '-' \
                                + str(j) \
                                + '-' \
                                +str(cost)
                            qs = Kakeibo.objects.get(code=code)
                            j += 1
                        j = 1
                        i += 1
                    while j <= month_2:
                        code = str(request.user) \
                            + str(i) \
                            + '-' \
                            + str(j) \
                            + '-' \
                            + str(cost)
                        qs = Kakeibo.objects.get(code=code)
                        j += 1
                    cost = COST[int(cost)]
                    context = {
                        'form': form,
                        'cost': cost,
                        }
                    return render(request, 'multi_delete.html', context)
                except ObjectDoesNotExist:
                    no_exist_frag = True
                    cost = COST[int(cost)]
                    context = {
                        'form': form,
                        'i': i,
                        'j': j,
                        'cost': cost,
                        'no_exist_frag': no_exist_frag,
                        }
                    return render(request, 'multi_delete_start.html', context)
            context = {
                'form': form,
                'year_month_frag': year_month_frag,
                }
            return render(request, 'multi_delete_start.html', context)
    else:
        form = MultiDeleteForm()
    context = {'form': form}
    return render(request, 'multi_delete_start.html', context)

@login_required
def multi_delete(request):
    # まとめて削除
    form = MultiDeleteForm(request.POST)
    qs_list = []
    cost = request.POST['cost']
    year_1 = int(request.POST['year_1'])
    year_2 = int(request.POST['year_2'])
    month_1 = int(request.POST['month_1'])
    month_2 = int(request.POST['month_2'])
    i = year_1
    j = month_1
    if year_1 == year_2:
        while j <= month_2:
            code = str(request.user) \
                + str(year_1) \
                + '-' \
                + str(j) \
                + '-' \
                + str(cost)
            qs = Kakeibo.objects.get(code=code)
            qs.delete()
            j += 1
        cost = COST[int(cost)]
        context = {
            'form': form,
            'cost': cost,
            }
        return render(request, 'multi_delete_success.html', context)
    elif year_1 < year_2:
        while int(i) < year_2:
            while int(j) <= 12:
                code = str(request.user) \
                    + str(i) \
                    + '-' \
                    + str(j) \
                    + '-' \
                    + str(cost)
                qs = Kakeibo.objects.get(code=code)
                qs.delete()
                j += 1
            j = 1
            i += 1
        while j <= month_2:
            code = str(request.user) \
                + str(i) \
                + '-' \
                + str(j) \
                + '-' \
                + str(cost)
            qs = Kakeibo.objects.get(code=code)
            qs.delete()
            j += 1
        cost = COST[int(cost)]
        context = {
            'cost': cost,
            'form': form,
            }
        return render(request, 'multi_delete_success.html', context)
    
@login_required
def database(request, num=1):
# データ一覧
    all_data = Kakeibo.objects.all().filter(owner=request.user).order_by('-date')
    page = Paginator(all_data, 10)
    context = {
        'all_data': page.get_page(num),
        }
    return render(request, 'database.html', context)

def get_graph():
# グラフ作成　graphのなかで使用される関数
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x, y, label):
# グラフ作成　graphのなかで使用される関数
    sns.set(font=["Meiryo", "Yu Gothic", "Hiragino Maru Gothic Pro"])
    plt.switch_backend('AGG')
    plt.figure(figsize=(10,5), dpi=100)
    plt.title('年間の推移')
    plt.plot(x, y, label=label, marker='*')
    plt.legend()
    month_list = list(range(1, 13))
    plt.xticks(month_list)
    plt.xlabel('月')
    plt.ylabel('金額')
    plt.tight_layout()
    graph = get_graph()
    return graph

def comparison_get_plot(year_list, x_list, y_list, cost):
# 複数グラフ作成の関数　multi_graphの中で使用される
    sns.set(font=["Meiryo", "Yu Gothic", "Hiragino Maru Gothic Pro"])
    plt.switch_backend('AGG')
    plt.figure(figsize=(10,5), dpi=100)
    plt.title(cost)
    month_list = list(range(1, 13))
    for year, x, y in zip(year_list, x_list, y_list):
        plt.plot(x, y, label=year, marker='*')
    plt.legend()
    plt.xticks(month_list)
    plt.xlabel('月')
    plt.ylabel('金額')
    plt.tight_layout()
    graph = get_graph()
    return graph

@login_required
# グラフ
def graph(request):
    if request.method == 'POST':
        form = GraphForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            cost = form.cleaned_data['cost']
            qs = Kakeibo.objects.filter(year=year, cost=cost, owner=request.user)
            qs = qs.order_by('month') 
            x = [x.month for x in qs]
            y = [y.money for y in qs]
            label = year + '年' + COST[int(cost)]
            chart = get_plot(x, y, label)
            month_list = list(range(1, 13))
            cost_list = []
            for i in range(1, 13):
                if qs.filter(month=i).exists():
                    cost_list.append(qs.get(month=i).money)
                else:
                    cost_list.append('-')
            if qs.aggregate(Sum('money'))['money__sum'] is not None:
                sum = qs.aggregate(Sum('money'))['money__sum']
                cost_list.append(sum)
            else:
                cost_list.append('-')    
            context = {
                'form': form,
                'month_list': month_list,
                'cost_list': cost_list,
                'chart': chart,
                }
            return render(request, 'graph.html', context)
    else:
        form = GraphForm()
    context = {'form': form}
    return render(request, 'graph_start.html', context)

@login_required
def comparison_start(request):
    if request.method == 'POST':
        form_1 = ChoiceYearForm(request.POST)
        if form_1.is_valid():   
            form_2 = ComparisonForm()
            cost = COST[int(form_1.cleaned_data['cost'])]
            years = int(form_1.cleaned_data['how_many_years'])
            context = {
                'form_1': form_1,
                'form_2': form_2,
                'cost': cost,
                'years': years,
            }
            return render(request, 'comparison_start_2.html', context)
    else:
        form_1 = ChoiceYearForm()
    context = {'form_1': form_1}
    return render(request, 'comparison_start.html', context)

@login_required
def comparison(request):
    form_1 = ChoiceYearForm(request.POST)
    form_2 = ComparisonForm(request.POST)
    if form_1.is_valid() and form_2.is_valid():   
        cost = form_1.cleaned_data['cost']
        qs = Kakeibo.objects.filter(cost=cost, owner=request.user)
        month_list = list(range(1, 13))
        year_list = []
        for year in form_2.cleaned_data.values():
            if year != '':
                year_list.append(int(year))
        # money_list    : テーブル用。フォームで指定された支出項目の金額をリストに格納。存在しないデータは'-'とする。
        # x             : グラフのx軸用。月をリストで格納。存在しないデータは含めない。
        # y             : グラフのy軸用。金額をリストで格納。存在しないデータは含めない。
        # moneys        : テーブル用。1年分ごとに作成されるmoney_listを外側のループで再び一つのリストにする。
        # x_list, y_list: グラフ用。moneysと同様に、x、yを外側のループで再び一つのリストにする。
        moneys = []
        x_list = []
        y_list = []
        for i in year_list:
            money_list = []
            x = []
            y = []
            for j in month_list:
                if qs.filter(year=i, month=j).exists():
                    money_list.append(qs.get(year=i, month=j).money)
                    x.append(j)
                    y.append(qs.get(year=i, month=j).money)
                else:
                    money_list.append('-')
            if qs.filter(year=i).aggregate(Sum('money'))['money__sum'] is not None:
                each_year_sum = qs.filter(year=i).aggregate(Sum('money'))['money__sum']
            else:
                each_year_sum = '-'
            money_list.append(each_year_sum)
            moneys.append(money_list)
            x_list.append(x)
            y_list.append(y)
        
        money_dict = dict(zip(year_list, moneys))
        cost = COST[int(cost)]
        chart = comparison_get_plot(year_list, x_list, y_list, cost)
        years = int(form_1.cleaned_data['how_many_years'])
        context = {
            'form_2': form_2,
            'month_list': month_list,
            'year_list': year_list,
            'money_dict': money_dict,
            'chart': chart,
            'cost': cost,
            'years': years,
        }
        return render(request, 'comparison.html', context)

@login_required
def table(request):
    # テーブル表示
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            qs = Kakeibo.objects.filter(year=year, owner=request.user)
            month_list = list(range(1, 13))
            cost_list = list(COST.values())
            # each_cost_sum:項目ごとの年間支出合計金額のリスト
            each_cost_sum = [qs.filter(cost=i).aggregate(Sum('money'))['money__sum'] for i in range(1, 10)]
            for i in range(9):
                if each_cost_sum[i] is None:
                    each_cost_sum[i] = '-'
            # 月毎の合計額のリスト
            each_month_sum = [qs.filter(month=i).aggregate(Sum('money'))['money__sum'] for i in range(1, 13)]
            for i in range(12):
                if each_month_sum[i] is None:
                    each_month_sum[i] = '-'
            # money_list:年間の支出金額リスト（項目ごとに別リストを作成）
            # moneys:内側のループ内で作成したそれぞれの項目に対するmoney_listを外側のループで再び一つのリストへまとめる
            moneys = []
            for i in range(1, 10):
                money_list = []
                for j in range(1, 13):
                    if qs.filter(cost=i, month=j).exists():
                        money_list.append(qs.get(cost=i, month=j).money)
                    else:
                        money_list.append('-')
                # 年間の合計額をmoney_listの最後に追加
                money_list.append(each_cost_sum.pop(0))
                moneys.append(money_list)
            money_dict = dict(zip(cost_list, moneys))
            # 年間の合計
            if qs.aggregate(Sum('money'))['money__sum'] is not None:
                all_sum = qs.aggregate(Sum('money'))['money__sum']
            else:
                all_sum = '-'
            context = {
                'form': form,
                'year': year,
                'month_list': month_list,
                'cost_list': cost_list,
                'money_dict': money_dict,
                'each_month_sum': each_month_sum,
                'all_sum': all_sum,
                }
            return render(request, 'table.html', context)            
    else:
        form = TableForm()
    context = {'form': form}
    return render(request, 'table_start.html', context)
