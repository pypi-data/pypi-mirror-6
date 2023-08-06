"""URLs for the dashboard_app app."""
from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^$',
        views.DashboardView.as_view(),
        name='dashboard_app_dashboard'),
    url(r'^get-outdated/$',
        views.DashboardLastUpdateView.as_view(),
        name='dashboard_app_get_last_updates'),
    url(r'^widget/$',
        views.DashboardRenderWidgetView.as_view(),
        name='dashboard_app_render_widget'),
    url(r'^api/widget/$',
        views.DashboardGetRemoteWidgetView.as_view(),
        name='dashboard_app_remote_widget'),
)
