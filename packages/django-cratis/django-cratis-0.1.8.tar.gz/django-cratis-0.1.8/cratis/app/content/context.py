from cratis.app.content.models import Banner


def banner_context(request):
    return {
        'banners': dict([(page.name, page) for page in Banner.objects.all()]),
    }