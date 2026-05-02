from django.urls import path
from . import views

urlpatterns = [
    path('zonas_conservacion/', views.ZonaConservacionView.as_view(), name='zonas_conservacion'),
    path('red_canales/', views.RedCanalView.as_view(), name='red_canales'),
    path('estaciones_monitoreo/', views.EstacionMonitoreoView.as_view(), name='estaciones_monitoreo'),
]