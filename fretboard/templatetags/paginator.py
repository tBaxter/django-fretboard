from django import template

register = template.Library()


@register.inclusion_tag('fretboard/includes/paginator.html', takes_context=True)
def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.
    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic view.
    """
    current_page = context.get('page')
    paginator    = context.get('paginator')
    if not paginator:
        return
    pages        = paginator.num_pages
    current_range = range(current_page - adjacent_pages, current_page + adjacent_pages + 1)
    page_numbers = [n for n in current_range if n > 0 and n <= pages]
    slugtype = ''

    if 'topic_slug' in context:
        page_url = context["topic"].get_short_url()
        slugtype = 'topic'
    elif 'forum_slug' in context:
        page_url = '/forum/%s/' % context["forum_slug"]
        slugtype = 'forum'
    else:
        page_url = context['request'].get_full_path()

    return {
        "is_paginated": context["is_paginated"],
        "page": current_page,
        "pages": pages,
        "page_obj": context['page_obj'],
        "page_numbers": page_numbers,
        "has_next": context["page_obj"].has_next(),
        "has_previous": context["page_obj"].has_previous(),
        "page_url" : page_url,
        'slugtype' : slugtype,
    }
