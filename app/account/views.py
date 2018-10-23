import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse


def log_in(request):
    """
    账号登录
    :param request:
    :return: json {'is_login': True, 'message': ''}
    """
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    message = {'is_login': False, 'message': ''}
    if user is not None:
        login(request, user)
        message['is_login'] = True
    else:
        message['message'] = '登录失败'
    message = json.dumps(message)
    return JsonResponse(message)


def log_out(request):
    """
    账号登出
    :param request:
    :return:
    """
    logout(request)
    return JsonResponse(json.dumps({
        'is_logout': True,
        'message': '登出成功'
    }))
