from django.urls import path, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from app.account import views

router = routers.SimpleRouter()
router.register('user', views.RealUserViewSets)
router.register('delete-user', views.DeleteRealUser, base_name='delete-user')

urlpatterns = [
    path('', include(router.urls)),
    path('create-user/', views.CreateRealUser.as_view({'post': 'create'})),

    # 获取账户ID列表
    path('id-list/', views.RealUserIdList.as_view()),
    # 获取id1至id2之间的全部账户信息
    path('detail/<int:id1>/<int:id2>/', views.RealUserDetailId1AndId2List.as_view()),

    # jwt
    # 登录获取token
    path('login/', obtain_jwt_token),
    # 刷新token
    path('token-refresh/', refresh_jwt_token),
    # 验证token
    path('token-verify/', verify_jwt_token),
]
