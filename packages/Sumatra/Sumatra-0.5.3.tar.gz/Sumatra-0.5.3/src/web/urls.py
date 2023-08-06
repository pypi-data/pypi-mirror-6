"""
Define URL dispatching for the Sumatra web interface.
"""

from django.conf.urls.defaults import *
from django.conf import settings
from sumatra.web.views import Timeline, ProjectListView

P = {
    'project': r'(?P<project>\w+[\w ]*)',
    'label': r'(?P<label>\w+[\w|\-\.:]*)',
}

urlpatterns = patterns('sumatra.web.views',
    (r'^$', ProjectListView.as_view()),
    (r'^%(project)s/$' % P, 'list_records'),
    (r'^%(project)s/about/$' % P, 'show_project'),
    (r'^%(project)s/delete/$' % P, 'delete_records'),
    (r'^%(project)s/tag/$' % P, 'list_tags'),
    (r'^%(project)s/%(label)s/$' % P, 'record_detail'),
    (r'^%(project)s/%(label)s/datafile$' % P, 'show_file'),
    (r'^%(project)s/%(label)s/download$' % P, 'download_file'),
    (r'^%(project)s/%(label)s/image$' % P, 'show_image'),
    (r'^%(project)s/%(label)s/diff/(?P<package>[\w_]+)*$' % P, 'show_diff'),
    (r'^%(project)s/simulation$' % P, 'run_sim'),
    (r'^%(project)s/settings$' % P, 'settings'), 
    (r'^%(project)s/search$' % P, 'search'),
    (r'^%(project)s/settags$' % P, 'set_tags'),
)

urlpatterns += patterns('',
    #(r'^timeline/(?P<user>\w+[\w ]*)/', Timeline.as_view()), 
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
