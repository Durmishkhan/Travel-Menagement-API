from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'trips', views.TripViewSet, basename='trip')
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')
router.register(r'expense-summaries', views.ExpenseSummaryViewSet, basename='expense-summary')


urlpatterns = router.urls











# urlpatterns = [
#     path("trips/", views.TripListCreate.as_view(), name = "trip-list"),
#     path("trips/delete/<int:pk>/", views.TripDestroyApiView.as_view(), name = "trip-delete"),
#     path("trips/update/<int:pk>/", views.TripUpdateView.as_view(), name = "trip-update" ),
#     path("trips/<int:trip_id>/expenses/", views.ExpenseListCreateView.as_view(), name='add-expenses'),
#     path("trips/<int:trip_id>/total-expense/", views.ExpenseListCreateView.as_view(), name='view-total-expense'),
#     path("locations/", views.LocationCreateApiView.as_view(), name = "location-list" ),
#     path("locations/delete-update/<int:pk>/", views.LocationDestroyUpdateApiView.as_view(),name = "location-delete-update"),
#     path("expense/delete/<int:pk>/", views.TripDestroyApiView.as_view(), name='expense-delete'),
#     path("expense/update/<int:pk>/", views.ExpenseUpdateApiView.as_view(), name='expense-update')
# ]

