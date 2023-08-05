import datetime
import json

from django.shortcuts import (
    render_to_response,
    get_object_or_404)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    Http404)
from django.core import urlresolvers
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext

from omblog.decorators import (
    cache_page,
    login_required)
from omblog.models import (
    Post,
    Tag,
    PostImage)
from omblog.forms import (
    CreatePostForm,
    EditPostForm,
    PostImageForm)
from omblog import settings as om_settings


def json_response(x, status=200):
    return HttpResponse(
        json.dumps(x, sort_keys=True, indent=2),
        content_type='application/json; charset=UTF-8',
        status=status)


def login(request):
    """Authenticates a user and logs them in"""


@login_required
def redirect_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return HttpResponseRedirect(
        urlresolvers.reverse('omblog:edit', args=[post.pk]))


@csrf_exempt
@login_required
def attach_delete(request):
    try:
        pk = int(request.POST.get('pk'))
    except ValueError:
        raise Http404()

    if request.method == 'POST':
        image = get_object_or_404(PostImage, pk=pk)
        image.src.delete()
        image.delete()
        return json_response({'success': True})
    return json_response({'success': False})


@csrf_exempt
@login_required
def attach(request):
    # if the post does not exist, throw a wobbler
    post = get_object_or_404(Post, pk=request.POST.get('post'))

    # now make the form
    attachments = []
    for filename, phile in request.FILES.items():
        form = PostImageForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.src = phile
            attachment.post = post
            attachment.save()
            attachments.append({
                'pk': attachment.pk,
                'thumb': attachment.thumb(),
                'large': attachment.large(),
            })

    # make the response
    success = True if len(attachments) > 0 else False

    # work on a better means of error handling
    return json_response({
        'success': success,
        'attachments': attachments})


@csrf_exempt
@login_required
def create(request):
    form = CreatePostForm()
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save()
            response_dict = {
                'success': True,
                'url': post.edit_url()}
        else:
            response_dict = {
                'success': False,
                'errors': dict(form.errors.items())}
        return json_response(response_dict)

    return render_to_response('omblog/create.html', {
        'form': form,
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def edit(request, pk):
    # get the post
    post = get_object_or_404(Post, pk=pk)
    form = EditPostForm(instance=post)

    # handle post
    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            response = {'success': True, 'slug': post.slug}
            return json_response(response)

        # deal with the errors
        return json_response({
            'success': False,
            'errors': dict(form.errors.items())})

    return render_to_response('omblog/edit.html', {
        'post': post,
        'form': form,
    }, context_instance=RequestContext(request))


@cache_page
def tag(request, slug):
    # get the tag
    try:
        tag = Tag.objects.get(slug=slug)
    except Tag.DoesNotExist:
        raise Http404('no tag found')
    except Tag.MultipleObjectsReturned:
        tag = Tag.objects.filter(slug=slug)[0]

    posts = Post.objects.visible(user=request.user)
    posts = posts.filter(tags=tag)

    return render_to_response('omblog/tags.html', {
        'posts': posts,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
        'tag': tag
    }, context_instance=RequestContext(request))


@cache_page
def index(request):
    """The index"""
    posts = Post.objects.visible(user=request.user)

    if posts.count() > om_settings.INDEX_ITEMS:
        posts = posts[:om_settings.INDEX_ITEMS]

    return render_to_response('omblog/index.html', {
        'posts': posts,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
    }, context_instance=RequestContext(request))


@cache_page
def month(request, year, month):
    """The month archive"""
    date = datetime.date(year=int(year), month=int(month), day=1)
    posts = Post.objects.visible(user=request.user).filter(
        created__year=year,
        created__month=month)

    return render_to_response('omblog/month.html', {
        'posts': posts,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
        'date': date
    }, context_instance=RequestContext(request))


@cache_page
def post(request, slug):
    """view post"""
    try:
        post = Post.objects.visible(user=request.user)\
            .select_related('tags').get(slug=slug)
    except Post.DoesNotExist:
        raise Http404

    return render_to_response('omblog/post.html', {
        'post': post,
        'dates': Post.objects.dates(),
        'tags': Tag.objects.tags_and_counts(),
    }, context_instance=RequestContext(request))
