from django.urls import path, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from app.account import views

router = routers.SimpleRouter()
router.register('user', views.RealUserViewSets, base_name='user')
router.register('department', views.DepartmentViewSets, base_name='department')
urlpatterns = [
    path('', include(router.urls)),

    # 获取账户ID列表
    path('id-list/', views.RealUserIdList.as_view(), name='user-id-list'),
    # 获取id1至id2之间的全部账户信息
    path('some-user-detail/', views.RealUserSomeUserDetailIList.as_view(), name='some-user-detail'),

    # jwt
    # 登录获取token
    path('login/', obtain_jwt_token, name='login'),
    # 刷新token
    path('token-refresh/', refresh_jwt_token),
    # 验证token
    path('token-verify/', verify_jwt_token),
]
