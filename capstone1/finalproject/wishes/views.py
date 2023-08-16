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
from django.utils import timezone
import atexit
import threading
import time
from django.utils import timezone


from .models import User, Profile




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

    if request.method == 'POST':
        code = request.POST.get('access_code')

        if not code:
            # No password provided, show error message
            return render(request, "wishes/description.html", {
                "message": "Please enter a password",
                "vote": vote
            })

        if code == vote.access_code:
            # Password is correct, proceed to show voting options
            return render(request, "wishes/description.html", {
                "message": "Correct",
                "vote": vote,

                "password_correct": True
            })
        else:
            # Password is incorrect, show error message
            return render(request, "wishes/description.html", {
                "message": "Invalid password, try again.",
                "vote": vote
            })

    # Handle GET request by showing the description page
    return render(request, "wishes/description.html", {
        "vote": vote
    })



@login_required
def voting_view(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)
    
    # Check if the user has already voted in this voting
    has_voted = Choose_option.objects.filter(user=request.user, option_text__vote=vote).exists()
    
    if request.method == 'POST':
        selected_option_id = request.POST.get('selected_option')
        selected_option = get_object_or_404(VoteOption, id=selected_option_id)
        
        if not has_voted:
            vote.selected_option = selected_option
            vote.save()
            Choose_option.objects.create(user=request.user, option_text=selected_option, has_voted=True)
            return redirect('voting_results', vote_id=vote_id)
        else:
            # You can handle the case where the user has already voted, for example, showing an error message.
            return render(request, "wishes/not_vote.html")

    # Check if the closing datetime has passed and update the status if needed
    if vote.closing_datetime and timezone.now() > vote.closing_datetime and vote.status == 'open':
        vote.status = 'closed'
        vote.save()

    return render(request, "wishes/voting_view.html", {
        "vote": vote,
        "has_voted": has_voted,  # Pass the has_voted status to the template
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
    user_votes = Create_vote.objects.filter(user=user)  # Cambio en esta línea
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


@login_required
def new_survey(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_votes = user.created_votes.all()

    if request.method == 'POST':
        name_vote = request.POST.get('nameVote')
        description = request.POST.get('description')
        image_vote = request.FILES.get('imageVote')
        access_code = request.POST.get('access_code')
        closing_vote = request.POST.get('closingVote')  # Obtener el valor de closingVote

        if name_vote and access_code: 
            vote = Create_vote.objects.create(
                user=user,
                nameVote=name_vote,
                description=description,
                imageVote=image_vote,
                access_code=access_code,
                closingVote=closing_vote  # Asignar el valor de closingVote al campo de cierre de votación
            )

            option_text_list = request.POST.getlist('option_text[]')
            description_vote_list = request.POST.getlist('description_vote')
            image_description_list = request.FILES.getlist('image_description')

            max_length = max(len(option_text_list), len(description_vote_list), len(image_description_list))

            for i in range(max_length):
                option_text = option_text_list[i] if i < len(option_text_list) else ''
                description_vote = description_vote_list[i] if i < len(description_vote_list) else ''
                image_description = image_description_list[i] if i < len(image_description_list) else None

                if option_text.strip() or description_vote.strip() or image_description:
                    VoteOption.objects.create(
                        vote=vote,
                        option_text=option_text,
                        description_vote=description_vote,
                        image_description=image_description
                    )

            return redirect('vote')
        else:
            error_message = "Invalid data provided. Please fill in required fields."
            return render(request, "wishes/new_survey.html", {
                "user": user,
                "user_votes": user_votes,
                "error_message": error_message
            })

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


@login_required
def vote(request):
    user = request.user
    votes_user = Create_vote.objects.filter(user=user)
    
    paginator = Paginator(votes_user, 5)
    
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

def close_expired_votes():
    while True:
        now = timezone.now()
        expired_votes = Create_vote.objects.filter(closingVote__lte=now, status='open')
        for vote in expired_votes:
            vote.status = 'closed'
            vote.save()
        time.sleep(5)  

# Crear un hilo para la función close_expired_votes
close_expired_thread = threading.Thread(target=close_expired_votes, daemon=True)
close_expired_thread.start()

# Registra la función close_expired_votes para que se ejecute al finalizar el proceso
atexit.register(lambda: close_expired_thread.join())


@login_required
def change_status(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)

    # Verificar si la votación ha expirado
    if vote.closingVote and timezone.now() >= vote.closingVote:
        if vote.status != 'closed':
            vote.status = 'closed'
            vote.save()

    return redirect('more_votes', vote_id=vote.id)

@login_required
def close_vote(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)

    # Verificar que el usuario que solicita el cierre sea el creador de la votación
    if request.user == vote.user:
        if vote.status != 'closed':
            vote.status = 'closed'
            vote.save()

    return redirect('more_votes', vote_id=vote.id)

def more_votes(request, vote_id):
    vote = get_object_or_404(Create_vote, id=vote_id)

    if vote.status == 'closed':
        # Obtener todas las opciones de voto relacionadas con la votación y contar la cantidad de votos para cada opción
        option_counts = VoteOption.objects.filter(vote=vote).annotate(count=Count('chosen_by'))
        # Ordenar las opciones de voto en orden descendente según la cantidad de votos
        more_votes = option_counts.order_by('-count')
        # Obtener la mayor cantidad de votos
        max_votes = more_votes.first().count if more_votes else 0
        # Obtener todas las opciones empatadas (con la mayor cantidad de votos)
        top_vote_options = [option for option in more_votes if option.count == max_votes]

        # Verificar si hay un empate o si todas las opciones tienen cero votos
        if len(top_vote_options) > 1 or max_votes == 0:
            top_vote_options = None  # Hay un empate o todas las opciones tienen cero votos
        else:
            # Solo hay una opción con la mayor cantidad de votos
            top_vote_options[0].option_text += "    WINNER!"

    else:
        more_votes = None
        top_vote_options = None

    return render(request, 'wishes/more_votes.html', {
        'more_votes': more_votes,
        'top_vote_options': top_vote_options,
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("inprogress"))
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
        return HttpResponseRedirect(reverse("inprogress"))
    else:
        return render(request, "wishes/register.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
