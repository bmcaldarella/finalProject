from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

class User(AbstractUser):
    pass
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    image_profile = models.ImageField(default='default.jpeg')

    def __str__(self):
        return f"Profile {self.user.username}"

    def get_image_url(self):
        return self.image_profile.url if self.image_profile else '/path/to/default/image'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class VoteOption(models.Model):
    vote = models.ForeignKey('Create_vote', on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=200, blank=True)
    description_vote = models.CharField(max_length=700, default='Default Description', blank=True)
    image_description = models.ImageField(default="voteDefault.jpeg", blank=True)

    def get_image_description_url(self):
        return self.image_description.url if self.image_description else '/path/to/default/image_description'

    def __str__(self):
        return self.option_text

class Create_vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_votes")
    nameVote = models.CharField(max_length=100)
    description = models.CharField(max_length=700, default='Default Description', blank=True)
    imageVote = models.ImageField(default="default.png", blank=True)
    selected_option = models.ForeignKey(VoteOption, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=(('open', 'Open'), ('closed', 'Closed'),), default='open')
    access_code = models.CharField(max_length=100, null=True, blank=True)
    closingVote = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"vote {self.id} made by {self.user}"

    def get_image_url(self):
        return self.imageVote.url if self.imageVote else '/media/default.png'

    def close_vote(self):
        self.status = 'closed'
        self.save()

class Choose_option(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chosen_options")
    option_text = models.ForeignKey(VoteOption, on_delete=models.CASCADE, related_name='chosen_by')
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return f"User {self.user.username} chose option '{self.option_text}' in vote '{self.option_text.vote.nameVote}'"
