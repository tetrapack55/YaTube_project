from django.core.paginator import Paginator


POSTS_LIMIT = 10


def paginate(request, posts):
    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
