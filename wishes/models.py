from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    image_profile = models.ImageField(default='default.jpeg')

    def __str__(self):
        return f"Profile {self.user.username}"

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
        if self.image_description and hasattr(self.image_description, 'url'):
            return self.image_description.url
        else:
            return '/path/to/default/image_description'

    def __str__(self):
        return self.option_text

class Create_vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userAuthor")
    nameVote = models.CharField(max_length=300)
    description = models.CharField(max_length=700, blank=True)
    imageVote = models.ImageField(default="default.jpeg", blank=True)
    selected_option = models.ForeignKey(VoteOption, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('open', 'Open'), ('closed', 'Closed'),), default='open')

    def __str__(self):
        return f"vote {self.id} made by {self.user}"

    def get_image_url(self):
        if self.imageVote and hasattr(self.imageVote, 'url'):
            return self.imageVote.url
        else:
            return '/path/to/default/image'

    def close_vote(self):
        self.status = 'closed'
        self.save()

class Choose_option(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chosen_options")
    option_text = models.ForeignKey(VoteOption, on_delete=models.CASCADE, related_name='chosen_by')

    def __str__(self):
        return f"User {self.user.username} chose option '{self.option_text}' in vote '{self.option_text.vote.nameVote}'"
