from rest_framework import routers

from app.account import views

account_router = routers.DefaultRouter()
account_router.register('users', views.RealUserViewSet)
