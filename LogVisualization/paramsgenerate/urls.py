from django.urls import path
from . import views

urlpatterns = [
    path('frequencyparams', views.fre_params, name='自动获取频率参数'),
    path('intervalparams', views.interval_params, name='自动获取间隔参数'),
    path('restparams', views.rest_params, name='自动获取休眠时长参数'),
    path('diversityparams', views.diversity_params, name='自动获取多样性参数'),
]
