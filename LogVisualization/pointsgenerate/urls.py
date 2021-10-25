from django.urls import path
from . import views

urlpatterns = [
    path('frequencypoints', views.fre_points, name='获取各个ip在频率特征对应的点'),
    path('intervalpoints', views.interval_points, name='获取各个ip在间隔特征对应的点'),
    path('restpoints', views.rest_points, name='获取各个ip在睡眠时长特征对应的点'),
    path('diversitypoints', views.diversity_points, name='获取各个ip在多样性特征对应的点'),
    path('paramsdata', views.paramsdata, name='获取日志的参数信息'),

]
