from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import Context, RequestContext

from django.template.loader import get_template
from django_bookmarks.forms import *
from bookmarks.models import *


from datetime import datetime, timedelta

def main_page(request):
    shared_bookmarks = SharedBookmark.objects.order_by(
        '-date'
    )[:10]
    variables = RequestContext(request, {
        'shared_bookmarks': shared_bookmarks
    })
    return render_to_response('main_page.html', variables)

def user_page(request, username):
    #try:
    #    user = User.objects.get(username=username)
    #except:
    #    raise Http404('Requested user not Found.')
    user = get_object_or_404(User, username=username)
    bookmarks = user.bookmark_set.order_by('id')
    is_friend = Friendship.objects.filter(
        from_friend = request.user,
        to_friend = user
    )
    variables = RequestContext (request,{
        'bookmarks' : bookmarks,
        'username' : username,
        'show_tags' : True,
        'show_edit': username == request.user.username,
        'is_friend': is_friend
            
    })
    return render_to_response('user_page.html', variables)

def logout_page(request):
    logout (request)
    return HttpResponseRedirect('/')

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password = form.cleaned_data['password1'],
                email = form.cleaned_data['email']
            )
        return HttpResponseRedirect('/register/success/')
    else:
            form = RegistrationForm()
            variables = RequestContext(request, {
                'form' : form
            })
            return render_to_response(
                'registration/register.html',
                variables
            )
    
@login_required    
def bookmark_save_page(request):
    ajax = request.GET.has_key('ajax')
    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        if form.is_valid():
            bookmark = _bookmark_save(request,form)
            if ajax:
                variables = RequestContext(request, {
                    'bookmarks': [bookmark],
                    'show_edit': True,
                    'show_tags': True
                })
                return render_to_response('bookmark_list.html', variables)
            else:
                return HttpResponseRedirect(
                    '/user/%s/' % request.user.username
            )
        else:
            if ajax:
                return HttpResponse('failure')
    elif request.GET.has_key('url'):
        url = request.GET['url']
        title = ''
        tags = ''
        try:
            link = Link.objects.get(url=url)
            bookmark = Bookmark.objects.get(
                link = link,
                user = request.user
            )
            title = bookmark.title
            tags = ' '.join(
                tag.name for tag in bookmark.tag_set.all()
            )
        except ObjectDoesNotExist:
            pass
        form = BookmarkSaveForm({
            'url' : url,
            'title': title,
            'tags': tags
        })
    else:
        form = BookmarkSaveForm()
    variables = RequestContext(request, {
            'form': form
        })
    if ajax:
        return render_to_response(
            'bookmark_save_form.html', variables
        )
    else:
        return render_to_response('bookmark_save.html', variables)
    
def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    bookmarks = tag.bookmarks.order_by('-id')
    variables = RequestContext(request, {
        'bookmarks' : bookmarks,
        'tag_name' : tag_name,
        'show_tags' : True,
        'show_user' : True
    })
    return render_to_response('tag_page.html', variables)

def tag_cloud_page(request):
    MAX_WEIGHT = 5
    tags = Tag.objects.order_by('name')
    #Calculating tag, minimum and maximum count
    min_count = max_count = tags[0].bookmarks.count()
    for tag in tags:
        tag.count = tag.bookmarks.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count
    #Calculating count range. avoid dividing by zero
    range = float(max_count - min_count)
    if range == 0.0:
        range = 1.0
    #Calculating tag weights
    for tag in tags:
        tag.weight = int(
            MAX_WEIGHT * (tag.count - min_count)/ range
        )
    variables = RequestContext(request, {
        'tags': tags
    })
    return render_to_response('tag_cloud_page.html', variables)

def search_page(request):
    form = SearchForm()
    bookmarks = []
    show_results = False
    if request.GET.has_key('query'):
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query': query})
            bookmarks = \
            Bookmark.objects.filter(title__icontains=query)[:10]
    variables = RequestContext(request,{'form': form,
            'bookmarks': bookmarks,
            'show_results' : show_results,
            'show_tags': True,
            'show_user': True
    })
    if request.GET.has_key('ajax'):
        return render_to_response('bookmark_list.html', variables)
    else:
        return render_to_response('search_page.html',variables)

def _bookmark_save(request, form):
    #create or get link
    link, dummy = \
    Link.objects.get_or_create(url=form.cleaned_data['url'])
    #create or get bookmark
    bookmark, created = Bookmark.objects.get_or_create(
        user = request.user,
        link = link
    )
    #update bookmark title
    bookmark.title = form.cleaned_data['title']
    #if the book is being updated, clear old tag list
    if not created:
        bookmark.tag_set.clear()
    #create new tag list
    tag_names = form.cleaned_data['tags'].split()
    for tag_name in tag_names:
        tag, dummy = Tag.objects.get_or_create(name=tag_name)
        bookmark.tag_set.add(tag)
    
    #share on the main page if requested
    if form.cleaned_data['share']:
        shared_bookmark,  created = SharedBookmark.objects.get_or_create(
            bookmark = bookmark
        )
        if created:
            shared_bookmark.users_voted.add(request.user)
            shared_bookmark.save()
    
    
    #save bookmark to database and return it
    bookmark.save()
    return bookmark

def ajax_tag_autocomplete(request):
    if request.GET.has_key('q'):
        tags = \
        Tag.objects.filter(name__istartswith=request.GET['q'])[:10]
        return HttpResponse('\n'.join(tag.name for tag in tags))
    return HttpResponse()

@login_required
def bookmark_vote_page(request):
    if request.GET.has_key('id'):
        try:
            id =  request.GET['id']
            shared_bookmark = SharedBookmark.objects.get(id=id)
            user_voted = shared_bookmark.users_voted.filter(
                username = request.user.username
            )
            if not user_voted:
                shared_bookmark.votes += 1
                shared_bookmark.users_voted.add(request.user)
                shared_bookmark.save()
        except ObjectDoesNotExist:
            raise Http404('Bookmark not found.')
    if request.META.has_key('HTTP_REFERER'):
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect('/')


def popular_page(request):
    today = datetime.today()
    yesterday = today - timedelta(1)
    shared_bookmarks = SharedBookmark.objects.filter(
        date__gt = yesterday
    )
    shared_bookmarks = shared_bookmarks.order_by(
        '-votes'
    )[:10]
    variables = RequestContext(request, {
        'shared_bookmarks': shared_bookmarks
    })
    return render_to_response('popular_page.html', variables)

def bookmark_page(request, bookmark_id):
    shared_bookmark = get_object_or_404(
        SharedBookmark,
        id = bookmark_id
    )
    variables = RequestContext(request, {
        'shared_bookmark': shared_bookmark
    })
    return render_to_response('bookmark_page.html', variables)

def friends_page(request, username):
    user = get_object_or_404(User, username=username)
    friends = \
    [friendship.to_friend for friendship in user.friend_set.all()]
    friend_bookmarks = \
    Bookmark.objects.filter(user__in=friends).order_by('-id')
    variables = RequestContext(request, {
        'username': username,
        'friends':  friends,
        'bookmarks': friend_bookmarks[:10],
        'show_tags': True,
        'show_user': True
    })
    return render_to_response('friends_page.html',variables)

@login_required
def friend_add(request):
    if request.GET.has_key('username'):
        friend = \
           get_object_or_404(User, username=request.GET['username'])
        friendship = Friendship(
            from_friend = request.user,
            to_friend = friend
        )
        friendship.save()
        return HttpResponseRedirect(
            '/friends/%s' % request.user.username
        )
    else:
        raise Http404
        
@login_required
def friend_invite(request):
    if request.method == 'POST':
        form = FriendInviteForm(request.POST)
        if form.is_valid():
            invitation = Invitation(
                name = form.cleaned_data['name'],
                email = form.cleaned_data['email'],
                code = User.objects.make_random_password(20),
                sender = request.user
            )
            invitation.save()
            invitation.send()
            return HttpResponseRedirect('friend/invite')
    else:
        form = FriendInviteForm()
    variables = RequestContext(request, {
        'form': form
    })
    return render_to_response('friend_invite.html', variables)