from django.urls import path

from .views import (
    InsListView,
    InsCreateView,
    InsUpdateView,
    ins_delete,
    InsListViewDeleted,
    InsDetailView,
    InstructionDownloadView,
    SelfInsListView,
    InstructionRestoreView,
    CreateTagsView,
    delete_tag,
    get_suggested_tags,
)

urlpatterns = [
    path("delete_tag/<int:pk>/", delete_tag, name="delete_tag"),
    path("listCreateTags/", CreateTagsView.as_view(), name="create_tags"),
    path("listIns/", InsListView.as_view(), name="instruction_list"),
    path("selflistIns/", SelfInsListView.as_view(), name="self_instruction_list"),
    path(
        "listInsDeleted/", InsListViewDeleted.as_view(), name="instruction_list_deleted"
    ),
    path(
        "<int:instruction_id>/download/",
        InstructionDownloadView.as_view(),
        name="instruction_download",
    ),
    path("get_suggested_tags/", get_suggested_tags, name="get_suggested_tags"),
    path("createIns/", InsCreateView.as_view(), name="instruction_create"),
    path("updateIns/<int:pk>", InsUpdateView.as_view(), name="instruction_update"),
    path(
        "restore/<int:instruction_id>/",
        InstructionRestoreView.as_view(),
        name="restore_instruction",
    ),
    path("detailIns/<int:pk>", InsDetailView.as_view(), name="instruction_detail"),
    path("deleteIns/<int:pk>", ins_delete, name="instruction_delete"),
]
