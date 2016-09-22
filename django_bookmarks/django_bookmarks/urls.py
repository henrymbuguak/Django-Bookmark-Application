import os.path
from django.conf.urls import *
from django.views.generic import TemplateView

from bookmarks.views import *
from django_bookmarks.feeds import *


from django.contrib import admin
admin.autodiscover()

site_media = os.path.join(
os.path.dirname(__file__), 'site_media'
)
feeds = {
    'recent': RecentBookmarks
}
urlpatterns = patterns ('',
    # Examples:
    # url(r'^$', 'django_bookmarks.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    #Friends
    (r'^friends/(\w+)/$', friends_page),
    (r'^friend/add/$', friend_add),
    (r'^friend/invite/$', friend_invite),
                
    #feeds
    #(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
    #                         {'feed_dict': feeds}),
                        
    # Browsing
    (r'^$', main_page),
    (r'^user/(\w+)/$', user_page),
    (r'^tag/([^\s]+)/$', tag_page),
    (r'^tag/$', tag_cloud_page),
    (r'^search/$',search_page),
    (r'^vote/$', bookmark_vote_page),
    (r'^popular/$', popular_page),
    (r'^bookmark/(\d+)/$', bookmark_page),
                        
    #comments
                        
    (r'^comments/', include('django.contrib.comments.urls')),
                        
    #Session Management
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
    { 'document_root': site_media}),
    (r'^register/$', register_page),
    (r'register/success/$', TemplateView.as_view(template_name='registration/register_success.html'),
    #{'template': 'registration/register_success.html'}
    ),
    
    #Ajax
    (r'^ajax/tag/autocomplete/$', ajax_tag_autocomplete),
                        
    #Account management
    (r'^save/$', bookmark_save_page),

    url(r'^admin/', admin.site.urls),
              )
              