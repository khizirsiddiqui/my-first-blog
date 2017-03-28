from django.contrib import admin
from .models import Post, Comment, UserProfile, Tag

admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserProfile)
