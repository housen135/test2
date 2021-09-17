"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from bbs.settings import MEDIA_ROOT
from django.conf.urls import url
from django.contrib import admin

from app01 import views
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls,),
    url(r'^register/',views.register,name='register'),
    url(r'^login/',views.login,name='login'),
    url(r'^get_code/',views.get_code,name='getcode'),
    url(r'^home/',views.home,name='home'),
    url(r'^set_password',views.set_password,name='set_password'),
    url(r'^logout/',views.logout,name='logout'),
    url(r'^UpAndDown/',views.get_UpAndDown,name='get_UpAndDown'),
    url(r'^media/(?P<path>.*)',serve,{'document_root':MEDIA_ROOT}),
    url(r'^comment/',views.comment,name='comment'),
    url(r'^back_set',views.back_set,name='back_set'),
    url(r'^back_add',views.back_add,name='back_add'),
    url(r'^upload_img',views.upload_img),
    url(r'^set_img/',views.set_img),
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|date)/(?P<param>.*)/',views.site),
    url(r'^(?P<username>\w+)/$',views.site),
    url(r'^(?P<username>\w+)/(?P<article_id>\d+)',views.article_detail,name='article_detail'),
    
    

 
]
