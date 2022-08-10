from rest_framework import routers

from .views import CheckMyUserView
from django.urls import path, include

router = routers.DefaultRouter()
router.register('user', CheckMyUserView, basename='user')

urlpatterns = [
    path('', include(router.urls))
]
