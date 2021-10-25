from django.urls import path
from . import views

urlpatterns = [
    path('frequencydata', views.frequencydata, name='获取频率数据'),
    path('intervaldata', views.intervaldata, name='获取时间间隔数据'),
    path('onlinetimedata', views.onlinetimedata, name='获取时间间隔数据'),
    path('restdata', views.restdata, name='获取每日休息时长数据'),
    path('diversitydata', views.diversitydata, name='获取访问资源多样性特征'),
    path('periodismdata', views.periodismdata, name='获取访问资源周期性特征'),
    path('steplinedata', views.steplinedata, name='获取0-1序列图数据'),
]
