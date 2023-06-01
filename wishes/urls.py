from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("description/<int:vote_id>/", views.description, name="description"),
    path("votar/<int:vote_id>/", views.voting_view, name="voting_view"),
    path("editVote/<int:vote_id>/", views.editVote, name="edit_vote"),
    path("voting_results/<int:vote_id>/", views.voting_results, name="voting_results"),
    path("deleteVote/<int:vote_id>/", views.deleteVote, name="deleteVote"),
    path("inprogress/", views.inprogress, name="inprogress"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("user_votes/", views.vote, name="vote"),
    path("my_choose/", views.mychoose, name="my_choose"),
    path('change_status/<int:vote_id>/', views.change_status, name='change_status'),
    path('more_votes/<int:vote_id>/', views.more_votes, name='more_votes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
