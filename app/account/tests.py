import time

from django.contrib.auth import authenticate
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from app.account.models import RealUser, Department

admin_client = APIClient()
user_client = APIClient()
not_login_client = APIClient()


class AuthTests(APITestCase):
    """
    jwt认证测试
    """
    fixtures = ['account.json']

    login_url = reverse('login')
    admin_user = {'username': 'fawn', 'password': '1007'}
    error_user = {'username': 'fawn', 'password': '11111'}
    no_user_user = {'username': 'nouser', 'password': '123aaa123'}
    is_not_active_user = {'username': 'test1', 'password': '123aaa123'}
    user1 = {'username': 'test4', 'password': '123aaa123'}

    def test_login(self):
        """
        登录账户，包括管理员登录，普通用户登录，账号不存在，密码错误，已删除用户登录
        登录成功后设置认证，方便测试后续接口
        :return:
        """
        client = APIClient()

        response = admin_client.post(self.login_url, self.admin_user)
        self.assertTrue('token' in response.data.keys())
        admin_client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])

        response = user_client.post(self.login_url, self.user1)
        self.assertTrue('token' in response.data.keys())
        user_client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])

        response = client.post(self.login_url, self.no_user_user)
        self.assertEqual(response.data, {"non_field_errors": ["无法使用提供的认证信息登录。"]})

        response = client.post(self.login_url, self.error_user)
        self.assertEqual(response.data, {"non_field_errors": ["无法使用提供的认证信息登录。"]})

        response = client.post(self.login_url, self.is_not_active_user)
        self.assertEqual(response.data, {"non_field_errors": ["无法使用提供的认证信息登录。"]})

    def test_refresh_token(self):
        """
        测试刷新token
        """
        client = APIClient()
        response = client.post(self.login_url, self.admin_user)

        response = client.post(reverse('refresh-token'), response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RealUserTests(APITestCase):
    """
    账户测试
    """

    fixtures = ['account.json']

    register_user = {'username': 'test_register', 'password': '123aaa123'}
    register_haved_user = {'username': 'test4', 'password': '123aaa123'}

    def test_register(self):
        """
        尝试注册新账号及已有账号
        """
        client = APIClient()
        response = client.post(reverse('user-list'), self.register_user)
        self.assertEqual(response.data, {'username': 'test_register'})

        response = client.post(reverse('user-list'), self.register_haved_user)
        self.assertEqual(response.data, {"username": ["已存在一位使用该名字的用户。"]})

    def test_get_user(self):
        """
        不同权限用户获取账户信详细息
        """
        url1 = reverse('user-detail', args=[1])
        url2 = reverse('user-detail', args=[1000000])
        response = admin_client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = admin_client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = user_client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = user_client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = not_login_client.get(url1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = not_login_client.get(url2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_list(self):
        """
        获取用户列表信息，该URL不允许get访问
        """
        url = reverse('user-list')

        response = admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = not_login_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user(self):
        """
        更新性别为man或woman
        """
        url_id3 = reverse('user-detail', args=[3])
        url_id5 = reverse('user-detail', args=[5])

        update_id3_man = {'username': 'test2', 'sex': 'man'}
        update_id3_woman = {'username': 'test2', 'sex': 'woman'}
        update_id5_man = {'username': 'test4', 'sex': 'man'}
        update_id5_woman = {'username': 'test4', 'sex': 'woman'}

        update_id3_department_2 = {'username': 'test2', 'department': 2}
        update_id3_department_none = {'username': 'test2', 'department': ''}

        response = admin_client.put(url_id3, update_id3_man)
        self.assertEqual(response.data['sex'], 'man')
        response = admin_client.patch(url_id3, update_id3_woman)
        self.assertEqual(response.data['sex'], 'woman')

        response = user_client.put(url_id3, update_id3_man)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = user_client.patch(url_id3, update_id3_man)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = admin_client.put(url_id5, update_id5_man)
        self.assertEqual(response.data['sex'], 'man')
        response = admin_client.patch(url_id5, update_id5_woman)
        self.assertEqual(response.data['sex'], 'woman')

        response = user_client.put(url_id5, update_id5_man)
        self.assertEqual(response.data['sex'], 'man')
        response = user_client.patch(url_id5, update_id5_woman)
        self.assertEqual(response.data['sex'], 'woman')

        response = admin_client.patch(url_id3, update_id3_department_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = RealUser.objects.get(pk=3)
        self.assertEqual(user.department.id, 2)

        response = admin_client.patch(url_id3, update_id3_department_none)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = RealUser.objects.get(pk=3)
        self.assertEqual(user.department, None)

    def test_change_password(self):
        """
        尝试更改密码
        """
        url = reverse('user-change_password', args=[6])
        test_user_password1 = {'password': '123aaa111'}
        test_user_password2 = {'password': '123aaa123'}
        test_user_password3 = {'password': ''}
        client = APIClient()
        response = client.post(reverse('login'), {'username': 'test5', 'password': '123aaa123'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])

        response = client.post(url, test_user_password1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(authenticate(username='test5', password='123aaa111'))

        # 休眠3秒，等待可以正常使用新密码登录
        time.sleep(3)

        # 更改密码后使用原token获取当前账户信息
        response = client.get(reverse('user-detail', args=[6]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 重新登录
        response = client.post(reverse('login'), {'username': 'test5', 'password': '123aaa111'})
        client.credentials(HTTP_AUTHORIZATION='JWT ' + response.data['token'])

        response = client.post(url, test_user_password3)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = admin_client.post(url, test_user_password2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(authenticate(username='test5', password='123aaa123'))

        response = user_client.post(url, test_user_password2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tese_id_list(self):
        """
        不同权限用户尝试获取账户ID列表，仅管理员有权限
        """
        base_url = reverse('user-id-list')
        url_page = base_url
        url_page_1_size_none = base_url + '?page=1'
        url_page_2_size_none = base_url + '?page=2'
        url_page_1_size_2 = base_url + '?page=1&page_size=2'
        url_page_2_size_2 = base_url + '?page=2&page_size=2'
        url_page_2_size_1 = base_url + '?page=2&page_size=1'
        url_error_param = base_url + '?aaa=1'
        url_page_greater_than_max_page = base_url + '?page=10000'

        response = admin_client.get(url_page)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        no_param_response_data = response.data

        response = admin_client.get(url_page_1_size_none)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_page_2_size_none)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = admin_client.get(url_page_1_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['resultss']), 2)

        response = admin_client.get(url_page_2_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['resultss']), 2)

        response = admin_client.get(url_page_2_size_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['resultss']), 1)

        response = admin_client.get(url_error_param)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.data, no_param_response_data)

        response = admin_client.get(url_page_greater_than_max_page)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = user_client.get(url_page)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = not_login_client.get(url_page)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_some_user_detail(self):
        """
        获取id1至id2之间的全部账户信息，仅限管理员
        """
        base_url = reverse('some-user-detail')
        url_id1_1 = base_url + '?id1=1'
        url_id1_200 = base_url + '?id1=200'
        url_id2_3 = base_url + '?id2=3'
        url_id2_300 = base_url + '?id2=300'
        url_id1_2_id2_5 = base_url + '?id1=2&id2=5'
        url_id1_5_id2_2 = base_url + '?id1=5&id2=2'
        url_page_1 = base_url + '?page=1'
        url_page_2 = base_url + '?page=20'
        url_page_1_size_2 = base_url + '?page=1&page_size=2'
        url_id1_1_id2_5_page_2 = base_url + '?id1=1&id2=5&page=2'
        url_id1_1_id2_5_page_2_size_2 = base_url + '?id1=1&id2=5&page=2&page_size=2'

        response = admin_client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_id1_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_id1_200)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_id2_3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_id2_300)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_id1_2_id2_5)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 4)

        response = admin_client.get(url_id1_5_id2_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 4)

        response = admin_client.get(url_page_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_page_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = admin_client.get(url_page_1_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 2)

        response = admin_client.get(url_id1_1_id2_5_page_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = admin_client.get(url_id1_1_id2_5_page_2_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['results']), 2)

        response = user_client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = not_login_client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user(self):
        """
        管理员删除账户
        """
        url = reverse('user-detail', args=[5])

        response = user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = admin_client.delete(url)
        user = RealUser.objects.get(pk=5)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(user.is_active)


class DepartmentTests(APITestCase):
    """
    部门测试
    """
    fixtures = ['account.json']

    def test_get_department_list(self):
        """
        不同权限账户批量获取部门信息
        """
        base_url = reverse('department-list')
        url_page_2 = base_url + '?page=2'
        url_size_2 = base_url + '?page_size=2'
        url_page_2_size_2 = base_url + '?page=2&page_size=2'
        url_page_3_size_2 = base_url + '?page=3&page_size=2'

        response = admin_client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_page_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = admin_client.get(url_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_page_2_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.get(url_page_3_size_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = user_client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = user_client.get(url_page_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = user_client.get(url_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = user_client.get(url_page_2_size_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = user_client.get(url_page_3_size_2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = not_login_client.get(base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_department(self):
        """
        不同权限账户获取单部门信息
        """
        url = reverse('department-detail', args=[1])

        response = admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = not_login_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_department(self):
        """
        创建部门
        """
        url = reverse('department-list')
        department = {'name': 'test_create_department'}
        department_more_param = {'name': 'test_create_department_more_param', 'test_param': 'test'}
        department_haved = {'name': 'department3'}

        response = user_client.post(url, department)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = not_login_client.post(url, department)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = admin_client.post(url, department)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = admin_client.post(url, department_more_param)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = admin_client.post(url, department_haved)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_department(self):
        """
        更新部门信息
        """
        url_2 = reverse('department-detail', args=[2])
        url_3 = reverse('department-detail', args=[3])

        department_2_name = {'name': 'test_change_2'}
        department_2_name_patch = {'name': 'test_2_patch'}
        department_2_director = {'director': 2}
        department_3_name = {'name': 'test_change_3'}
        department_3_director_4 = {'director': 4}
        department_3_director_5 = {'director': 5}
        department_3_director_6_put = {'name': 'test_change_3', 'director': 6}
        department_3_director_7_put = {'name': 'test_change_3', 'director': 7}

        response = user_client.put(url_2, department_2_name)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = not_login_client.put(url_2, department_2_name)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = admin_client.put(url_2, department_2_name)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        department = Department.objects.get(pk=2)
        self.assertEqual(department.name, 'test_change_2')

        response = admin_client.patch(url_2, department_2_name_patch)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        department = Department.objects.get(pk=2)
        self.assertEqual(department.name, 'test_2_patch')

        response = admin_client.put(url_2, department_2_director)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = admin_client.put(url_3, department_3_name)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = admin_client.put(url_3, department_3_director_4)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # error TODO:// 修正patch方法
        # error start
        # response = admin_client.patch(url_3, department_3_director_4, content_type='application/json')
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #
        # response = admin_client.patch(url_3, department_3_director_5)
        # department = Department.objects.get(pk=3)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(department.director.id, 5)
        # erroe end

        response = admin_client.put(url_3, department_3_director_6_put)
        department = Department.objects.get(pk=3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(department.director.id, 6)

        # error
        # response = admin_client.put(url_3, department_3_director_7_put)
        # department = Department.objects.get(pk=3)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertEqual(department.director.id, 6)

    def test_delete_department(self):
        """
        删除部门
        """
        url_2 = reverse('department-detail', args=[2])
        url_3 = reverse('department-detail', args=[3])

        response = user_client.delete(url_2)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = not_login_client.delete(url_2)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = admin_client.delete(url_2)
        users = RealUser.objects.filter(department=2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(users), 0)

        response = admin_client.delete(url_3)
        users = RealUser.objects.filter(department=3)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(users), 0)
