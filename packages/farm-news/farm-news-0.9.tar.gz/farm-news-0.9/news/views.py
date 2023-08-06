from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Article
from .forms import ArticleSearchForm


def ArticleList(request):
    """
    This renders the list of articles.
    """

    # Setup the search form.
    form = ArticleSearchForm(request.GET)

    # If the form is valid, then we'll proceed and search.
    if form.is_valid() and request.GET:

        # Filter by category.
        if len(form.cleaned_data['category']) > 0:
            articles = Article.objects.published().filter(category__in=form.cleaned_data['category']).order_by('-publish_on')
        else:
            articles = Article.objects.published().order_by('-publish_on')

        # Filter by date
        if len(form.cleaned_data['date']) > 0:
            query = reduce(lambda a, b: a | b, [Q(publish_on__month=d.split('-')[1], publish_on__year=d.split('-')[0]) for d in form.cleaned_data['date']])
            articles = articles.filter(query)

    # If the form isn't valid (or there was no request.GET data), then just proceed with the product list.
    else:
        articles = Article.objects.published().order_by('-publish_on')

    # Setup the paginator.
    paginator = Paginator(articles, 6)
    page = paginator.page(request.GET.get('page', 1))

    # Grab the query_string
    qs = request.GET.copy()

    # Remove 'page', as this will be set in the template, and we don't want two keys
    # with potentially different values screwing up the paginator.
    if qs.has_key('page'):
        qs.pop('page')

    # Re-create the querystring.
    query_string = qs.urlencode()

    return render(request, 'news/article_list.html', {
        'form': form,
        'obj_list': articles,
        'paginator': paginator,
        'page': page,
        'query_string': query_string
    })


def ArticleDetail(request, slug):
    """
    View a single article.
    """
    article = get_object_or_404(Article, slug=slug)

    return render(request, 'news/article_detail.html', {
        'object': article,
    })
