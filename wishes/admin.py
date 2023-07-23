from django.contrib import admin

# Register your models here.
from .models import User,Profile,Create_vote,VoteOption,Choose_option

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Create_vote)
admin.site.register(VoteOption)
admin.site.register(Choose_option)
