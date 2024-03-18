from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from .forms import *
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required


# Create your views here.


def index(request):
    return render(request, "blog1/index.html")


def post_list(request, category=None):
    if category is not None:
        posts = Post.published.filter(category=category)
    else:
        posts = Post.published.all()
    paginator = Paginator(posts, 1)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    context = {
        'posts': posts,
        'category': category
    }
    return render(request, "blog1/list.html", context)


# post list

# class Postlistview(ListView):
#     queryset = Post.published.all()
#     context_object_name = "post"
#     paginate_by = 3
#     template_name = 'blog1/list.html'


# post detail
@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'comment': comments
    }
    return render(request, "blog1/detail.html", context)


# class PostDetailView(DetailView):
#     model = Post
#     template_name = "blog1/detail.html"


# ticket
@login_required
def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket_obj = Ticket.objects.create()
            cd = form.cleaned_data
            ticket_obj.message = cd['message']
            ticket_obj.name = cd['name']
            ticket_obj.email = cd['email']
            ticket_obj.phone = cd['phone']
            ticket_obj.subject = cd['subject']
            ticket_obj.save()
            return redirect("blog1:index")
    else:
        form = TicketForm()
    return render(request, "forms/ticket.html", {'form': form})


# comment post
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'post': post,
        'form': form,
        'comment': comment
    }
    return render(request, "forms/comment.html", context)


# create post
@login_required
def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_field=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_field=form.cleaned_data['image2'], post=post)
            return redirect('blog1:profile')
    else:
        form = CreatePostForm()
    return render(request, 'forms/create_post.html', {'form': form})


# search post
@login_required
def post_search(request):
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results1 = Post.published.annotate(similarity=TrigramSimilarity('title', query)).filter(
                similarity__gt=0.1).order_by('-similarity')
            results2 = Post.published.annotate(similarity=TrigramSimilarity('description', query)).filter(
                similarity__gt=0.1).order_by('-similarity')
            results = (results1 | results2)
    context = {
        'query': query,
        'results': results
    }

    return render(request, 'blog1/search.html', context)


# profile user
@login_required
def profile(request):
    user = request.user
    posts = Post.published.filter(author=user)
    return render(request, 'blog1/profile.html', {'posts': posts})


# delete post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog1:profile')
    return render(request, 'forms/delete-post.html', {'post': post})


# delete image
@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    image.delete()
    return redirect('blog1:profile')


# edit post
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            Image.objects.create(image_field=form.cleaned_data['image1'], post=post)
            Image.objects.create(image_field=form.cleaned_data['image2'], post=post)
            return redirect('blog1:profile')
    else:
        form = CreatePostForm(instance=post)
    return render(request, 'forms/create_post.html', {'form': form, 'post': post})


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return render(request, 'blog1/profile.html', {'form': form})
                else:
                    return HttpResponse('your not login')
            else:
                return HttpResponse('you are not logged in')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


# def logout(request):
#     logout(request)
#     return redirect(request.META.get('HTTP_REFERER'))


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Account.objects.create(user=user)
            return render(request, 'registration/register_done.html', {'user': user})
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def edit_account(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.POST, instance=request.user.account)
        if account_form.is_valid() and user_form.is_valid():
            account_form.save()
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)
    context = {
        'user_form': user_form,
        'account_form': account_form
    }

    return render(request, 'registration/edit_account.html', context)


def logout_user(request):
    if request.method == 'POST':
        form = LogoutForm(request.POST)
        if form.is_valid():
            return render(request, 'registration/logged_out.html')
    else:
        form = LogoutForm()
    return render(request, 'registration/logged_out.html', {'form': form})


def post_view(request):
    user_posts = Post.objects.filter(user=request.user)
    paginator = Paginator(user_posts, 3)
    page = request.GET.get('page')
    user_posts = paginator.get_page(page)
    return render(request, 'partilas/paginator.html', {'user_posts': user_posts})
