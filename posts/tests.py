from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User
from django.core.cache.utils import make_template_fragment_key


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

    def assert_origin_params(self, response, user, default_text, group):
        self.assertEqual(response.author, user)
        self.assertEqual(response.text, default_text)
        self.assertEqual(response.group, group)

    def assert_edit_params(self, response, user, new_text, new_group):
        self.assertEqual(response.author, user)
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

        for url in urls:
            response_url = self.auth_client.get(url)
            self.assertEqual(response_url.status_code, 200)
            if response_url.context.get('paginator') is not None:
                post_objects = response_url.context['page'][0]
            else:
                post_objects = response_url.context['post']
            self.assert_origin_params(post_objects, self.user, default_text, self.default_group)

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

        for url in urls:
            response_url = self.auth_client.get(url)
            self.assertEqual(response_url.status_code, 200)
            if response_url.context.get('paginator') is not None:
                post_objects = response_url.context['page'][0]
            else:
                post_objects = response_url.context['post']
            self.assert_edit_params(post_objects, self.user, new_text, new_group)

        response_group_origin = self.auth_client.get(reverse('group', kwargs={'slug': self.default_group.slug}))

        self.assertEqual(response_group_origin.context['paginator'].count, 0)

    def test_img(self):
        with open('media/tests/test_photo.jpg', 'rb') as img:
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

    # def test_500(self):
    #     response = self.auth_client.get(reverse('server_error'))
    #     print('-------')
    #     print(response)
    #     self.assertEqual(response.status_code, 500)
    #     # self.assertContains(response, 'Error handler content', status_code=500)

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
        cache.touch(key, 0)
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

        # post = Post.objects.first()
        # data = self.auth_client.get(reverse('post_concrete', kwargs={'username': second_user.username,
        #                                                              'post_id': post.id}))
        # print('//////////')
        # print(data.context['post'])

        # Оформление подписки
        self.auth_client.get(reverse('profile_follow', kwargs={'username': second_user.username}))
        response = self.auth_client.get(reverse('follow_index'))
        print('-*--*-*----*-*--*-++++')
        print(response)
        print(response.context['page'][0].author)
        print(response.context['page'][0].text)
        print(response.context['page'][0].group)
        self.assertEqual(response.context['page'][0].text, 'Текст поста второго автора -> TestMan_2')
        # self.assertContains(response, 'Текст поста второго автора -> TestMan_2', status_code=200, html=True)
