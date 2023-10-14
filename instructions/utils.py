from django.db.models import Q


def perform_search(
    queryset,
    search_query,
    tag_filter,
    type_filter,
    start_date_filter,
    end_date_filter,
    status_filter,
    include_deleted=False,
):
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    if tag_filter:
        queryset = queryset.filter(tags__name__icontains=tag_filter)

    if type_filter:
        queryset = queryset.filter(type=type_filter)

    if start_date_filter:
        queryset = queryset.filter(datetime_created__gte=start_date_filter)

    if end_date_filter:
        queryset = queryset.filter(datetime_created__lte=end_date_filter)

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    if not include_deleted:
        queryset = queryset.filter(is_active=True)

    return queryset
