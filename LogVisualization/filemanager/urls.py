from django.urls import path
from . import views

urlpatterns = [
    path('fileupload', views.fileUpload, name='处理文件上传'),
    path('getmetainfo', views.getMetaInfo, name='获取元信息'),
    path('filedel', views.fileDelete, name='删除文件')
]
