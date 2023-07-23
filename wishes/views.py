from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Create_vote, VoteOption, Choose_option
from .forms import EditVoteForm
from django.core.paginator import Paginator
from .models import User, Profile


def my_view(request):
    votes_user = Create_vote.objects.all()
    paginator = Paginator(votes_user, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'wishes/vote.html', {'page_obj': page_obj})


def index(request):
    allvote = Create_vote.objects.all()
    return render(request, "wishes/index.html", {
        "allvote": allvote
    })


def inprogress(request):
    search_query = request.GET.get('search')
    if search_query:
        allvote = Create_vote.objects.filter(nameVote__icontains=search_query)
    else:
        allvote = Create_vote.objects.all()
    return render(request, "wishes/in_progress.html", {
        "allvote": allvote
    })


def description(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)
    return render(request, "wishes/description.html", {
        "vote": vote
    })


def voting_view(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)

    if request.method == 'POST':
        selected_option_id = request.POST.get('selected_option')
        selected_option = get_object_or_404(VoteOption, id=selected_option_id)
        vote.selected_option = selected_option
        vote.save()
        Choose_option.objects.create(user=request.user, option_text=selected_option)
        return redirect('voting_results', vote_id=vote_id)

    return render(request, "wishes/voting_view.html", {
        "vote": vote
    })


def voting_results(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)
    option_counts = VoteOption.objects.filter(vote=vote).annotate(count=Count('chosen_by'))
    total_votes = option_counts.aggregate(total_votes=Sum('count'))['total_votes']
    option_percentages = []
    for option in vote.options.all():
        option_votes = option_counts.get(id=option.id).count
        option_percentages.append((option.option_text, option_votes))
    option_percentages = sorted(option_percentages, key=lambda x: x[1], reverse=True)
    if option_percentages:
        return render(request, "wishes/voting_results.html", {
            "vote": vote,
            "option_percentages": option_percentages,
            "total_votes": total_votes
        })
    else:
        return render(request, "wishes/voting_results.html", {
            "vote": vote,
            "option_percentages": option_percentages,
            "total_votes": total_votes,
            "no_votes": True
        })


@login_required
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user_votes = user.userAuthor.all()
    if request.method == 'POST':
        name_vote = request.POST.get('nameVote')
        description = request.POST.get('description')
        image_vote = request.FILES.get('imageVote')
        vote = Create_vote.objects.create(user=request.user, nameVote=name_vote, description=description, imageVote=image_vote)
        option_text = request.POST.getlist('option_text[]')
        description_vote = request.POST.getlist('description_vote')
        image_description = request.FILES.getlist('image_description')
        num_options = len(option_text)
        num_descriptions = len(description_vote)
        num_images = len(image_description)
        max_length = max(num_options, num_descriptions, num_images)
        option_text += [''] * (max_length - num_options)
        description_vote += [''] * (max_length - num_descriptions)
        image_description += [None] * (max_length - num_images)
        for i in range(max_length):
            options = VoteOption.objects.create(
                vote=vote,
                option_text=option_text[i],
                description_vote=description_vote[i],
                image_description=image_description[i]
            )
        return redirect('vote')
    return render(request, "wishes/profile.html", {
        "user": user,
        "user_votes": user_votes
    })


def new_survey(request, user_id):
    user = User.objects.get(pk=user_id)
    user_votes = user.userAuthor.all()
    if request.method == 'POST':
        name_vote = request.POST.get('nameVote')
        description = request.POST.get('description')
        image_vote = request.FILES.get('imageVote')
        vote = Create_vote.objects.create(user=request.user, nameVote=name_vote, description=description, imageVote=image_vote)
        option_text = request.POST.getlist('option_text[]')
        description_vote = request.POST.getlist('description_vote')
        image_description = request.FILES.getlist('image_description')
        num_options = len(option_text)
        num_descriptions = len(description_vote)
        num_images = len(image_description)
        max_length = max(num_options, num_descriptions, num_images)
        option_text += [''] * (max_length - num_options)
        description_vote += [''] * (max_length - num_descriptions)
        image_description += [None] * (max_length - num_images)
        for i in range(max_length):
            options = VoteOption.objects.create(
                vote=vote,
                option_text=option_text[i],
                description_vote=description_vote[i],
                image_description=image_description[i]
            )
        return redirect('vote')
    return render(request, "wishes/new_survey.html", {
        "user": user,
        "user_votes": user_votes
    })


@login_required
def mychoose(request):
    user = request.user
    user_options = VoteOption.objects.filter(chosen_by__user=user)
    return render(request, "wishes/my_choose.html", {
        "user_options": user_options
    })


def vote(request):
    user = request.user
    votes_user = Create_vote.objects.filter(user=user)
    paginator = Paginator(votes_user, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "wishes/vote.html", {
        "user": user,
        "votes_user": page_obj
    })


def deleteVote(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)
    vote.delete()
    return redirect('vote')


def editVote(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)
    if request.method == "POST":
        form = EditVoteForm(request.POST, request.FILES, instance=vote)
        if form.is_valid():
            form.save()
            option_texts = request.POST.getlist('option_text[]')
            descriptions = request.POST.getlist('description_vote')
            images = request.FILES.getlist('image_description')
            vote.options.all().delete()
            for i in range(len(option_texts)):
                option_text = option_texts[i]
                description = descriptions[i]
                image = images[i] if i < len(images) else None
                VoteOption.objects.create(
                    vote=vote,
                    option_text=option_text,
                    description_vote=description,
                    image_description=image
                )
            return redirect('description', vote_id=vote_id)
    else:
        form = EditVoteForm(instance=vote)
    return render(request, "wishes/edit_vote.html", {"form": form, "vote": vote})


@login_required
def change_status(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)
    vote.close_vote()
    return redirect('more_votes', vote_id=vote.id)


def more_votes(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)
    if vote.status == 'closed':
        option_counts = VoteOption.objects.filter(vote=vote).annotate(count=Count('chosen_by'))
        more_votes = option_counts.order_by('-count')
    else:
        more_votes = None
    return render(request, 'wishes/more_votes.html', {'more_votes': more_votes})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "wishes/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "wishes/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "wishes/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            profile_image = request.FILES.get('profile_image')
            banner_image = request.FILES.get('banner_image')
            profile = Profile.objects.get(user=user)
            if profile_image:
                profile.image = profile_image
            if banner_image:
                profile.ProfileBanner = banner_image
            profile.save()
        except IntegrityError:
            return render(request, "wishes/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "wishes/register.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
