from django import template

register = template.Library()

@register.filter
def get_star_color(rating_percentages, star_index):
    star_index -= 1
    if star_index in rating_percentages:
        return 'text-yellow-500' if rating_percentages[star_index + 1] > 0 else 'text-gray-300'
    return 'text-gray-300' 