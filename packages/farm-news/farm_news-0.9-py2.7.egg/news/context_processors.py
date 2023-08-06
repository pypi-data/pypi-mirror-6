from django.conf import settings

from .models import Article


def latest_articles(request):
    num_latest_articles = hasattr(settings, 'NUM_LATEST_ARTICLES') and \
        settings.NUM_LATEST_ARTICLES or 3
    objs = Article.objects.published().order_by('-publish_on')[:num_latest_articles]

    return {
        'latest_articles': objs
    }
