from django.urls import path

from . import views

urlpatterns = [
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("resetPass/", views.PassRecoveryView.as_view(), name="recoveryPass"),
    path("changePass/<int:pk>/", views.change_password, name="changePass"),
    path("userListBehvarz/", views.BehvarzListView.as_view(), name="behvarz_list"),
    path("userListExpert/", views.ExpertListView.as_view(), name="expert_list"),
    path("userListManager/", views.ManagerListView.as_view(), name="manager_list"),
    path(
        "incompleteUser/",
        views.UserIncompleteRegisterView.as_view(),
        name="incomplete_list",
    ),
    # path('behvarz-search/', behvarz_search, name='behvarz-search'),
    path(
        "registerBehvarz/", views.BehvarzRegisterView.as_view(), name="behvarz_register"
    ),
    path("registerExpert/", views.ExpertRegisterView.as_view(), name="expert_register"),
    path(
        "registerManager/", views.ManagerRegisterView.as_view(), name="manager_register"
    ),
    path(
        "deleteBehvarz/<int:pk>/",
        views.BehvarzDeleteView.as_view(),
        name="behvarz_delete",
    ),
    path(
        "deleteExpert/<int:pk>/", views.ExpertDeleteView.as_view(), name="expert_delete"
    ),
    path(
        "deleteManager/<int:pk>/",
        views.ManagerDeleteView.as_view(),
        name="manager_delete",
    ),
    path(
        "editBehvarz/<int:pk>/",
        views.BehvarzUpdateView.as_view(),
        name="behvarz_update",
    ),
    path(
        "editExpert/<int:pk>/", views.ExpertUpdateView.as_view(), name="expert_update"
    ),
    path(
        "editManager/<int:pk>/",
        views.ManagerUpdateView.as_view(),
        name="manager_update",
    ),
    path(
        "editProvince/<int:pk>",
        views.ProvinceUpdateView.as_view(),
        name="province_edit",
    ),
    path(
        "delProvince/<int:pk>",
        views.ProvinceDeleteView.as_view(),
        name="province_delete",
    ),
    path("addListProvince/", views.ProvinceAddView.as_view(), name="province_add_list"),
    path("editCity/<int:pk>", views.CityUpdateView.as_view(), name="city_edit"),
    path("delCity/<int:pk>", views.CityDeleteView.as_view(), name="city_delete"),
    path("addListCity/<int:pk>", views.province_city, name="city_add_list"),
    path(
        "editHealthCenterEdit/<int:pk>",
        views.HealthCenterUpdateView.as_view(),
        name="hc_edit",
    ),
    path(
        "delHealthCenter/<int:pk>",
        views.HealthCenterDeleteView.as_view(),
        name="hc_delete",
    ),
    path("addListCenter/<int:pk>", views.healthcenteraddview, name="hc_add_list"),
    path(
        "editVillage/<int:pk>", views.VillageUpdateView.as_view(), name="village_edit"
    ),
    path(
        "delVillage/<int:pk>", views.VillageDeleteView.as_view(), name="village_delete"
    ),
    path(
        "addListVillage/<int:pk>", views.village_add_list_view, name="village_add_list"
    ),
    path("palcesTable/", views.PLacesTableView.as_view(), name="places_table"),
]
