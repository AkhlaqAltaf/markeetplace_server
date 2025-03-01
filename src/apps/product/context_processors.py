from src.apps.product.models import Category, Brand


def menu_categories(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    brands = Brand.objects.all()
    return {'categories': categories,'brands':brands}

