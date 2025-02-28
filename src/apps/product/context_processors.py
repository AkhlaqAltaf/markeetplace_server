from src.apps.product.models import Category


def menu_categories(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return {'categories': categories}