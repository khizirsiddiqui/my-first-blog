from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings as django_settings

import os.path


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('S', 'Select'),
        ('M', 'Male'),
        ('F', 'Female'),
    )
    user = models.OneToOneField(User, related_name='user')
    website = models.URLField(default='', blank=True)
    bio = models.TextField(default='', blank=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    city = models.CharField(max_length=100, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    organization = models.CharField(max_length=100, default='', blank=True)
    reputation = models.BigIntegerField(default=0)
    Likers = models.ManyToManyField(User, related_name='liker', default=None)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, default='S')

    def repAdd(self, liker):
        self.reputation += 1
        self.save()
        self.Likers.add(liker)

    def __str__(self):
        return self.user.username

    def user_rep(self):
        return self.reputation

    def user_likers(self):
        return self.Likers.all()

    def get_picture(self):
        no_picture = django_settings.STATIC_URL + 'avatars/default.png'
        filename = django_settings.MEDIA_ROOT + \
            '/profile_pictures/' + self.user.username + '.jpg'
        picture_url = django_settings.MEDIA_URL + \
            'profile_pictures/' + self.user.username + '.jpg'
        if os.path.isfile(filename):
            return picture_url
        else:
            return no_picture


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = UserProfile(
            user=user, bio='My bio - I am still thinking')
        user_profile.save()


post_save.connect(create_profile, sender=User)


class Tag(models.Model):
    title = models.CharField(max_length=200, unique=True, default='')
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return '{0} - '.format(self.title)


class Post(models.Model):

    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)
    upvotes = models.IntegerField(default=0)
    upvoters = models.ManyToManyField('auth.User', related_name='upvoters')
    views = models.BigIntegerField(default=0)
    tags = models.ManyToManyField(Tag)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def viewed(self):
        self.views += 1
        self.save()

    def upvote(self, upvoter):
        if upvoter not in self.upvoters.all():
            self.upvotes += 1
            self.upvoters.add(upvoter)
            self.save()
            return True
        else:
            return False

    def get_upvoter(self):
        return self.upvoters.all()

    def approved_comments(self):
        return self.comments.filter(approved_comment=True)

    def __str__(self):
        return '{0} - {1}'.format(self.title, self.author)


class Comment(models.Model):
    post = models.ForeignKey('blog.Post', related_name='comments')
    author = models.CharField(max_length=20)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def __str__(self):
        return '{0} - {1}'.format(self.author, self.post.title)
