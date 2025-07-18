from django.urls import path
from . import views


urlpatterns = [
    path("trips/", views.TripListCreate.as_view(), name = "trip-list"),
    path("trips/delete/<int:pk>/", views.TripDestroyApiView.as_view(), name = "trip-delete"),
    path("trips/update/<int:pk>/", views.TripUpdateView.as_view(), name = "trip-update" ),
    path("locations/", views.LocationCreateApiView.as_view(), name = "location-list" ),
    path("locations/delete-update/<int:pk>/", views.LocationDestroyUpdateApiView.as_view(),name = "location-delete-update"),
    path("trips/<int:trip_id>/expenses/", views.ExpenseListCreateView.as_view()),
    path("expense/delete/<int:pk>/", views.TripDestroyApiView.as_view(), name='expense-delete'),
    path("expense/update/<int:pk>/", views.ExpenseUpdateApiView.as_view(), name='expense-update')
]

