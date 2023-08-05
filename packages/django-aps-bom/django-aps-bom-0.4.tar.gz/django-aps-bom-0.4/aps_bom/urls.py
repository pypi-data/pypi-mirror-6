"""URLs for the aps_bom app."""
from django.conf.urls import patterns, url

from .views import BOMUploadView, CBOMDownloadView, CBOMUploadView


urlpatterns = patterns(
    '',
    url(r'^cbom/upload/$', CBOMUploadView.as_view(),
        name='aps_bom_cbom_upload'),
    url(r'^bom/download/(?P<cbom_pk>\d+)/$', CBOMDownloadView.as_view(),
        name='aps_bom_cbom_download'),
    url(r'^bom/download/$', CBOMDownloadView.as_view(),
        name='aps_bom_cbom_download'),
    url(r'^bom/upload/$', BOMUploadView.as_view(),
        name='aps_bom_bom_upload'),
)
