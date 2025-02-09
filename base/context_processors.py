from .models import Category, SiteInfo
from django.core.cache import cache


def category_context(request):
    categories = Category.objects.prefetch_related('child').all()
    return {'categories': categories}




def site_info_context(request):
    site_info = cache.get('site_info')

    if not site_info:
        site_info = SiteInfo.objects.first()
        cache.set('site_info', site_info, timeout=3600)

    return {'site_info': site_info}
