from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=50,
        unique=True,
    )
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Поля со * обязательны для заполнения',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Название группы',
        help_text='',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author} {self.group} {self.pub_date}'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Поля со * обязательны для заполнения',
    )
    created = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        models.UniqueConstraint(fields=['user', 'author'], name='following_unique')
        # uniqueConstraint = ('-pub_date',)
        # models.UniqueConstraint(fields=['app_uuid'])
        # models.UniqueConstraint('author')
        # UniqueConstraint(fields=['chambre', 'date'], name='reservation_unique')

