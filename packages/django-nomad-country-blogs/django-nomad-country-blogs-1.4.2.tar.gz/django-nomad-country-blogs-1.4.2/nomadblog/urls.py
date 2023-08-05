from django.conf.urls import patterns, url
from nomadblog.views import PostList, PostDetail, PostsByCategoryList, CategoriesList


urlpatterns = patterns(
    '',
    url(r'^$', PostList.as_view(), name='post_list'),
    url(r'^categories/$', CategoriesList.as_view(), name='category_list'),
    url(r'^categories/(?P<category_slug>[-\w]+)/$', PostsByCategoryList.as_view(), name='post_list_by_category'),
    url('^(?P<slug>[-\w]+)/$', PostDetail.as_view(), name='post_detail'),
)
