from django_filters import rest_framework as rest_filter
from rest_framework import views, filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Course, Module, Subject, Like, Comment, Rating
from .serializers import (CoursesListSerializer, CourseDetailSerializer, CreateCourseSerializer,
                          SubjectsListSerializer, SubjectDetailSerializer, CreateSubjectSerializer,
                          ModuleSerializer, CommentSerializer, RatingSerializer, )
from .permissions import IsAdminUser, IsAuthor, IsAuthorOrIsAdmin


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectsListSerializer
        elif self.action == 'retrieve':
            return SubjectDetailSerializer
        return CreateSubjectSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return []
        return [IsAdminUser()]


class CoursesFilter(rest_filter.FilterSet):
    created = rest_filter.DateTimeFromToRangeFilter()

    class Meta:
        model = Course
        fields = ('created', )


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CreateCourseSerializer
    filter_backends = [
        rest_filter.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title', 'overview', 'subject']
    ordering_fields = ['created', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return CoursesListSerializer
        elif self.action == 'retrieve':
            return CourseDetailSerializer
        return CreateCourseSerializer

    @action(['POST'], detail=True)
    def like(self, request, pk=None):
        course = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(course=course, user=user)
            like.is_liked = not like.is_liked
            if like.is_liked:
                like.save()
            else:
                like.delete()
            message = 'like' if like.is_liked else 'dislike'
        except Like.DoesNotExist:
            Like.objects.create(course=course, user=user, is_liked=True)
            message = 'liked'
        return Response(message, status=200)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return []
        elif self.action == 'create' or self.action == 'like':
            return [IsAuthenticated()]
        return [IsAuthorOrIsAdmin()]


class ModuleViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthorOrIsAdmin]


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'update':
            return [IsAuthor()]
        return [IsAuthorOrIsAdmin()]


class RatingViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthor()]
