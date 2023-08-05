from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.exceptions import ObjectDoesNotExist


class Country(models.Model):
    code = models.CharField(_('iso country code'), max_length=2, help_text='Reference: http://www.iso.org/iso/home/standards/country_codes/country_names_and_code_elements_txt.htm')
    name = models.CharField(_('name'), max_length=100)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class BlogHub(models.Model):
    name = models.CharField(_('blog hub'), max_length=100)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _('blog hub')
        verbose_name_plural = _('blog hubs')


class Blog(models.Model):
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)
    description = models.TextField(_('description'))
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    countries = models.ManyToManyField(Country, verbose_name=_('countries'))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='BlogUser', verbose_name=_('users'))
    hubs = models.ManyToManyField(BlogHub, verbose_name=_('hubs'))
    seo_title = models.CharField(_('seo title'), max_length=70, blank=True)
    seo_desc = models.CharField(_('seo meta description'), max_length=160, blank=True)

    class Meta:
        verbose_name = _('blog')
        verbose_name_plural = _('blogs')

    def __unicode__(self):
        return u"%s" % self.title


class BlogUser(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))
    slug = models.SlugField(_('slug'), max_length=50)
    blog = models.ForeignKey(Blog, verbose_name=_('blog'))
    bio = models.CharField(_('bio'), max_length=255, blank=True)
    seo_title = models.CharField(_('seo title'), max_length=70, blank=True)
    seo_desc = models.CharField(_('seo meta description'), max_length=160, blank=True)

    def __unicode__(self):
        return u"%s - %s" % (self.user.username, self.blog)

    class Meta:
        unique_together = ('slug', 'blog')
        verbose_name = _('blog user')
        verbose_name_plural = _('blog users')


class Category(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=50, unique=True)
    description = models.CharField(_('description'), max_length=500)
    seo_title = models.CharField(_('seo title'), max_length=70, blank=True)
    seo_desc = models.CharField(_('seo meta description'), max_length=160, blank=True)

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')


class Post(models.Model):
    PUBLIC_STATUS = 0
    DRAFT_STATUS = 1
    PRIVATE_STATUS = 2
    DEFAULT_POST_STATUS_CHOICES = (
        (PUBLIC_STATUS, 'public'),
        (DRAFT_STATUS, 'draft'),
        (PRIVATE_STATUS, 'private'),
    )
    POST_STATUS_CHOICES = getattr(settings, 'POST_STATUS_CHOICES', DEFAULT_POST_STATUS_CHOICES)

    bloguser = models.ForeignKey(BlogUser, verbose_name=_('blog user'))
    title = models.CharField(_('title'), max_length=300)
    slug = models.SlugField(_('slug'), max_length=50)
    pub_date = models.DateTimeField(_('publication date'), auto_now_add=True)
    status = models.IntegerField(_('status'), choices=POST_STATUS_CHOICES, default=0)
    categories = models.ManyToManyField(Category, verbose_name=_('categories'), blank=True)
    content = models.TextField(_('content'))
    featured_countries = models.ManyToManyField(Country, verbose_name=_('featured countries'), blank=True)

    def __unicode__(self):
        return u"%s - %s" % (self.bloguser, self.title)

    class Meta:
        abstract = True
        unique_together = ('bloguser', 'slug')
