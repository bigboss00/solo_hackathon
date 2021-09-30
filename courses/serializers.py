from rest_framework import serializers

from .models import Course, Module, Subject, Comment, Rating, Favourite


class SubjectsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'title')


class CoursesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'subject', 'title', 'overview', 'avr_rating', )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['likes'] = instance.likes.count()
        return rep


class ModulesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'


class CourseDetailSerializer(serializers.ModelSerializer):
    modules = ModulesListSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'subject', 'title', 'overview', 'created', 'avr_rating', 'modules', )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['like'] = instance.likes.count()
        rep['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        return rep


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ('user', )

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        if request.user.is_anonymous:
            raise serializers.ValidationError('Can create only authorized user')
        return super().create(validated_data)


class ModuleSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Course.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Module
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class SubjectDetailSerializer(serializers.ModelSerializer):
    courses = CoursesListSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ('id', 'title', 'courses')


class CreateSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Course.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'course', 'text', 'user', )

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Course.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ('id', 'rate', 'course', 'user', )

    def validate(self, attrs):
        course = attrs.get('course')
        request = self.context.get('request')
        user = request.user
        if Rating.objects.filter(course=course, user=user).exists():
            raise serializers.ValidationError('Impossible to rate twice')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class FavouriteCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = ('course', 'id')

        def get_favourite(self, obj):
            if obj.favourite:
                return obj.favourite
            return ''

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep['favourite'] = self.get_favourite(instance)
            return rep
