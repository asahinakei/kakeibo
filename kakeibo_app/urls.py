from django.urls import path, include
        
from .views import index
from .views import entry, edit_start_from_entry, edit_from_entry
from .views import multi_entry
from .views import database
from .views import table
from .views import graph
from .views import comparison, comparison_start
from .views import edit_start, edit
from .views import delete_start, delete
from .views import del_start_from_multi_entry, del_from_multi_entry
from .views import multi_delete_start, multi_delete

app_name = 'kakeibo_app'
urlpatterns = [
    # ホームページ
    path('', index, name='index'),
    path('index/', index, name='index'),
    # 入力
    path('entry/', entry, name='entry'),
    path('multi_entry/', multi_entry, name='multi_entry'),
    # テーブル・グラフ・データ一覧
    path('table/', table, name='table'),
    path('graph/', graph, name='graph'),
    path('comparison/', comparison, name='comparison'),
    path('comparison_start/', comparison_start, name='comparison_start'),
    path('database/', database, name='database'),
    path('database/<int:num>/', database, name='database'),
    # 編集
    path('edit_start/', edit_start, name='edit_start'),
    path('edit/', edit, name='edit'),
    path('edit_start_from_entry/', edit_start_from_entry, name='edit_start_from_entry'),
    path('edit_from_entry/', edit_from_entry, name='edit_from_entry'),
    # 削除
    path('delete_start/', delete_start, name='delete_start'),
    path('delete/', delete, name='delete'),
    path('del_start_from_multi_entry/', del_start_from_multi_entry, name='del_start_from_multi_entry'),
    path('del_from_multi_entry/', del_from_multi_entry, name='del_from_multi_entry'),
    path('multi_delete_start/', multi_delete_start, name='multi_delete_start'),
    path('multi_delete/', multi_delete, name='multi_delete'),
]