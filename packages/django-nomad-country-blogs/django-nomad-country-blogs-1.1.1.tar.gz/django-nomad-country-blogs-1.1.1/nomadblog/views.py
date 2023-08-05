from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.conf import settings

from nomadblog.models import Blog, Category
from nomadblog import get_post_model


DEFAULT_STATUS = getattr(settings, 'PUBLIC_STATUS', 0)
POST_MODEL = get_post_model()


class NomadBlogMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.blog = get_object_or_404(Blog, countries__code__iexact=self.kwargs.get('country_code'), slug=self.kwargs.get('blog_slug'))
        return super(NomadBlogMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(NomadBlogMixin, self).get_context_data(*args, **kwargs)
        context['blog'] = self.blog
        return context


class PostList(NomadBlogMixin, ListView):
    model = POST_MODEL
    template_name = 'nomadblog/post_list.html'

    def get_queryset(self):
        qs = super(PostList, self).get_queryset()
        return qs.filter(bloguser__blog=self.blog)


class PostDetail(NomadBlogMixin, DetailView):
    model = POST_MODEL
    template_name = 'nomadblog/post_detail.html'

    def get_object(self, queryset=None):
        queryset = self.get_queryset().filter(bloguser__blog=self.blog)
        return super(PostDetail, self).get_object(queryset)


class CategoriesList(NomadBlogMixin, ListView):
    model = Category


class PostsByCategoryList(NomadBlogMixin, ListView):
    model = POST_MODEL
    template_name = 'nomadblog/post_list_by_category.html'

    def get_queryset(self, *args, **kwargs):
        qs = super(PostsByCategoryList, self).get_queryset()
        self.category = get_object_or_404(Category, slug=self.kwargs.get('category_slug', ''))
        return qs.filter(categories=self.category)

    def get_context_data(self, *args, **kwargs):
        context = super(PostsByCategoryList, self).get_context_data(*args, **kwargs)
        context['category'] = self.category
        return context
