from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
import py_compile
import binascii
import io


class ProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestMan',
            email='TestMan.s@skynet.com',
            password='12345')

        self.default_group = Group.objects.create(
            title='buildings',
            slug='builds',
            description='About builds & towns'
        )

        self.auth_client = Client()
        self.auth_client.force_login(self.user)

        self.not_auth_client = Client()

    def assert_params(self, urls, default_text, new_text, new_group):
        for url in urls:
            response_url = self.auth_client.get(url)
            self.assertEqual(response_url.status_code, 200)
            if response_url.context.get('paginator') is not None:
                response = response_url.context['page'][0]
            else:
                response = response_url.context['post']

            self.assertEqual(response.author, self.user)
            if not (new_text and new_group):
                self.assertEqual(response.text, default_text)
                self.assertEqual(response.group, self.default_group)
            else:
                self.assertEqual(response.text, new_text)
                self.assertEqual(response.group, new_group)

    def test_profile(self):
        response_profile = self.auth_client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response_profile.status_code, 200)

    def test_auth_user_new_post(self):
        default_text = 'Test text'
        response = self.auth_client.post(reverse('new_post'),
                                         data={
                                             'text': default_text,
                                             'group': self.default_group.id,
                                         },
                                         )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, default_text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.default_group)

    def test_not_auth_user_new_post(self):
        default_text = 'Test text'
        response = self.not_auth_client.post(reverse('new_post'),
                                             data={
                                                 'text': default_text,
                                             },
                                             )
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('new_post')}", status_code=302)
        self.assertEqual(Post.objects.count(), 0)

    def test_new_post_on_pages(self):
        default_text = 'Test text'
        response = self.auth_client.post(reverse('new_post'),
                                         data={
                                             'author': self.user,
                                             'text': default_text,
                                             'group': self.default_group.id,
                                         },
                                         )
        self.assertEqual(response.status_code, 302)

        post_conc = Post.objects.last()

        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('group', kwargs={'slug': self.default_group.slug}),
            reverse('post_concrete', kwargs={'username': self.user.username, 'post_id': post_conc.id}),
        )

        self.assert_params(urls, default_text, new_text=None, new_group=None)

    def test_post_and_group_edit(self):
        default_text = 'Test text'
        new_text = 'edit TEXT!!!'
        new_group = Group.objects.create(
            title='Muscle_Cars',
            slug='cars',
            description='About cars'
        )
        response = self.auth_client.post(reverse('new_post'),
                                         data={
                                             'text': default_text,
                                             'group': self.default_group.id,
                                         }
                                         )
        self.assertEqual(response.status_code, 302)

        post_conc = Post.objects.last()

        response = self.auth_client.post(reverse('post_edit',
                                                 kwargs={'username': post_conc.author,
                                                         'post_id': post_conc.id
                                                         }
                                                 ),
                                         data={
                                             'text': new_text,
                                             'group': new_group.id,
                                         },
                                         )

        self.assertEqual(response.status_code, 302)

        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('group', kwargs={'slug': new_group.slug}),
            reverse('post_concrete', kwargs={'username': self.user.username, 'post_id': post_conc.id}),
        )

        self.assert_params(urls, default_text, new_text, new_group)

        response_group_origin = self.auth_client.get(reverse('group', kwargs={'slug': self.default_group.slug}))
        self.assertEqual(response_group_origin.context['paginator'].count, 0)

    def test_img(self):
        img_in_bytes = (b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x02\x01\x01'
                        b'\x02\x01\x01\x02\x02\x02\x02\x02\x02\x02\x02\x03\x05\x03\x03\x03\x03\x03\x06\x04\x04\x03'
                        b'\x05\x07\x06\x07\x07\x07\x06\x07\x07\x08\t\x0b\t\x08\x08\n\x08\x07\x07\n\r\n\n\x0b\x0c\x0c'
                        b'\x0c\x0c\x07\t\x0e\x0f\r\x0c\x0e\x0b\x0c\x0c\x0c\xff\xdb\x00C\x01\x02\x02\x02\x03\x03\x03'
                        b'\x06\x03\x03\x06\x0c\x08\x07\x08\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c'
                        b'\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c'
                        b'\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\xff\xc0\x00\x11\x08\x00\x01\x00'
                        b'\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01'
                        b'\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4'
                        b'\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00'
                        b'\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n'
                        b'\x16\x17\x18\x19\x1a%&\'('
                        b')*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95'
                        b'\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9'
                        b'\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3'
                        b'\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01'
                        b'\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05'
                        b'\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04'
                        b'\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1'
                        b'\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'('
                        b')*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94'
                        b'\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8'
                        b'\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3'
                        b'\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01'
                        b'\x00\x02\x11\x03\x11\x00?\x00\xf9\xae\x8a(\xaf\xc0\xcf\xf6\x80\xff\xd9')

        img = SimpleUploadedFile('test_red.jpg', img_in_bytes)
        default_text = 'Test text'
        new_text = 'edit TEXT!!!'
        new_group = Group.objects.create(
            title='Muscle_Cars',
            slug='cars',
            description='About cars'
        )
        response = self.auth_client.post(reverse('new_post'),
                                         data={
                                             'text': default_text,
                                             'group': self.default_group.id,
                                         }
                                         )
        self.assertEqual(response.status_code, 302)

        post_conc = Post.objects.last()

        response = self.auth_client.post(reverse('post_edit',
                                                 kwargs={'username': post_conc.author,
                                                         'post_id': post_conc.id
                                                         }
                                                 ),
                                         data={
                                             'text': new_text,
                                             'image': img,
                                             'group': new_group.id,
                                         },
                                         )
        self.assertEqual(response.status_code, 302)

        urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post_concrete', kwargs={'username': self.user.username, 'post_id': post_conc.id}),
            reverse('group', kwargs={'slug': self.default_group.slug}),
        )

        for url in urls:
            response_url = self.client.get(url)
            self.assertContains(response_url, '<img')

    def test_404(self):
        response = self.auth_client.get(reverse('page_not_found'))
        self.assertEqual(response.status_code, 404)

    def test_cache(self):
        default_text = 'Test text'
        key = make_template_fragment_key('index_page')

        response_old = self.auth_client.get(reverse('index'))
        self.auth_client.post(reverse('new_post'),
                              data={
                                  'text': default_text,
                                  'group': self.default_group.id,
                              }
                              )
        response_new = self.auth_client.get(reverse('index'))
        self.assertEqual(response_old.content, response_new.content)
        cache.clear()
        response_newest = self.auth_client.get(reverse('index'))
        self.assertNotEqual(response_old.content, response_newest.content)

    def test_view_post_with_follow(self):
        second_user = User.objects.create_user(
            username='TestMan_2',
            email='TestMan_2.s@skynet.com',
            password='123456789')
        self.auth_client.force_login(second_user)

        self.auth_client.post(
            reverse('new_post'),
            {'text': 'Текст поста второго автора -> TestMan_2',
             'group': self.default_group.id},
            )
        # Перелог на первого пользователя TestMan
        self.auth_client.force_login(self.user)
        # Оформление подписки
        self.auth_client.get(reverse('profile_follow', kwargs={'username': second_user.username}))
        # Страница с подписками
        response = self.auth_client.get(reverse('follow_index'))
        self.assertEqual(response.context['page'][0].text, 'Текст поста второго автора -> TestMan_2')
        self.assertEqual(response.context['page'][0].author, second_user)
        # self.assertContains(response, 'Текст поста второго автора -> TestMan_2', status_code=200, html=True)
