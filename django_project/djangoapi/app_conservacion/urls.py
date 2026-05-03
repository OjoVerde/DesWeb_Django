from django.urls import path
from . import views

urlpatterns = [
    path('api/zonas_conservacion/', views.ZonaConservacionView.as_view(), name='zonas_conservacion'),
    path('api/red_canales/', views.RedCanalView.as_view(), name='red_canales'),
    path('api/estaciones_monitoreo/', views.EstacionMonitoreoView.as_view(), name='estaciones_monitoreo'),
]