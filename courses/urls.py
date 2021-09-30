from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import CourseViewSet, ModuleViewSet, SubjectViewSet, CommentViewSet, RatingViewSet, FavouritesListView

router = SimpleRouter()
router.register('courses', CourseViewSet, 'courses')
router.register('modules', ModuleViewSet, 'modules')
router.register('subjects', SubjectViewSet, 'subjects')
router.register('comments', CommentViewSet, 'comments')
router.register('ratings', RatingViewSet, 'ratings')

urlpatterns = [
    path('', include(router.urls)),
    path('favourites_list/', FavouritesListView.as_view())
]
