from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill


class Category(models.Model):
    """
    Model for storing news categories.
    """
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_('The title of the category')
    )
    slug = models.SlugField(
        _('slug'),
        unique=True,
        help_text=_('Unique identifier for the category used in URLs')
    )
    order = models.IntegerField(default=0)

    class Meta:
        app_label = 'news'
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['order','title']

    def __unicode__(self):
        return self.title


class ArticleQuerySet(QuerySet):
    """
    Custom QuerySet for Article model.
    """
    def published(self):
        """
        Filter by Articles that are past their publish date and marked to be
        published.
        """
        return self.filter(publish_on__lte=timezone.now(), publish=True)


class ArticleManager(models.Manager):
    """
    Custom Manager for Article model.
    """
    use_for_related_fields = True

    def get_query_set(self):
        """
        Return custom QuerySet object instead of default.
        """
        return ArticleQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_query_set().published()


class Article(models.Model):
    """
    Model for storing a news article.
    """
    # Content
    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_('The title for the news article')
    )
    slug = models.SlugField(
        _('slug'),
        unique=True,
        help_text=_('Unique identifier for the article used in URLs')
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_('category'),
        related_name='articles',
        help_text=_('The category this article belongs to')
    )
    content = models.TextField(
        _('content'),
        help_text=_('Content for the news article')
    )
    image = models.ImageField(upload_to="news", blank=True, null=True)

    list_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(222, 150)],
        format='JPEG',
        options={'quality': 70}
    )
    detail_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(690, 265)],
        format='JPEG',
        options={'quality': 70}
    )



    # Publish
    publish = models.BooleanField(
        _('publish'),
        default=False,
        help_text=_('Check this if you wish to publish this article')
    )
    publish_on = models.DateTimeField(
        _('publish date'),
        default=timezone.now,
        help_text=_('The date from wish to publish this article')
    )

    # Record Details
    created_on = models.DateTimeField(
        _('created on'),
        help_text=_('The date and time the article was created')
    )
    updated_on = models.DateTimeField(
        _('updated on'),
        help_text=_('The date and time the article was last updated')
    )

    objects = ArticleManager()

    class Meta:
        app_label = 'news'
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ['-publish_on']

    def __unicode__(self):
        return self.title

    def save(self, *ar, **kw):
        """
        Update created_on and/or updated_on on save.
        """
        if not self.id:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        return super(Article, self).save(*ar, **kw)

    @models.permalink
    def get_absolute_url(self):
        return ('articles_detail', (), {'slug': self.slug})
