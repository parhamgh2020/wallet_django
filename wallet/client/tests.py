from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from .views import UserViewSet


class UserViewSetTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = UserViewSet.as_view({'get': 'list',
                                         'post': 'create',
                                         'patch': 'partial_update'})
        self.user_data = {'username': 'testuser',
                          'email': 'testuser@example.com',
                          'first_name': 'testuser',
                          'last_name': 'testuser'}
        self.user = User.objects.create_user(**self.user_data)

    def test_list(self):
        request = self.factory.get('/client/users/')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        self.new_user_data = {'username': 'newuser',
                          'email': 'testuser@example.com',
                          'first_name': 'newuser',
                          'last_name': 'newuser'}
        request = self.factory.post('/client/users/', self.new_user_data)
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username=self.new_user_data['username'])
        self.assertEqual(user.email, self.new_user_data['email'])

    def test_retrieve(self):
        request = self.factory.get(f'/client/users/{self.user.pk}/')
        response = self.view(request, pk=self.user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['username'],
                         self.user_data['username'])

    def test_update(self):
        new_email = 'newemail@example.com'
        request = self.factory.patch(f'/client/users/{self.user.pk}/', {'email': new_email})
        response = self.view(request, pk=self.user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(username=self.user_data['username'])
        self.assertEqual(user.email, new_email)
