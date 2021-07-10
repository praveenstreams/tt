from django.urls import path
from . import views
urlpatterns=[

    path("", views.home, name="home"),
    path("cam", views.cam, name="cam"),
    path('video_feed', views.video_feed, name='video_feed'),
    path('captured',views.capture,name='capture'),
    path('attend',views.attend,name='t_a'),
    path('video_feedv2',views.video_feedv2,name='name'),
    path('export',views.export,name='export'),
    path('clear',views.clear,name='clear')

]