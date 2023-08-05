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
    name = models.CharField(_('name'), max_length=255, blank=True)
    slug = models.SlugField(_('slug'), max_length=50)
    blog = models.ForeignKey(Blog, verbose_name=_('blog'))
    bio = models.CharField(_('bio'), max_length=255, blank=True)
    image = models.ImageField(_('image'), blank=True, null=True, upload_to="images/bloguser_avatars/%Y/%m/%d", max_length=255)
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

    pub_date.editable = True

    def __unicode__(self):
        return u"%s - %s" % (self.bloguser, self.title)

    class Meta:
        abstract = True
        unique_together = ('bloguser', 'slug')

    def validate_unique(self, *args, **kwargs):
        """post slug and blog slug must be unique in posts"""
        super(Post, self).validate_unique(*args, **kwargs)
        error_exc = ValidationError({NON_FIELD_ERRORS: ('Post with slug "%s" already exists for blog "%s"' % (self.slug, self.bloguser.blog), )})
        try:
            obj = self.__class__._default_manager.get(bloguser__blog__slug=self.bloguser.blog.slug, slug=self.slug)
        except ObjectDoesNotExist:
            return
        except self.__class__.MultipleObjectsReturned:
            raise error_exc
        else:
            if not obj.id == self.id:
                raise error_exc
