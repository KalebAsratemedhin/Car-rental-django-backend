from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Avg
from .models import Car, CarImage, Comment, Rating
from .serializers import (
    CarSerializer, CarImageSerializer,
    CommentSerializer, RatingSerializer
)
from .permissions import IsOwnerOrReadOnly, IsCarOwnerOrReadOnly

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def upload_images(self, request, pk=None):
        car = self.get_object()
        images = request.FILES.getlist('images')
        is_primary = request.data.get('is_primary', False)

        if not images:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_instances = []
        for image in images:
            image_instance = CarImage.objects.create(
                car=car,
                image=image,
                is_primary=is_primary and len(image_instances) == 0
            )
            image_instances.append(image_instance)

        serializer = CarImageSerializer(image_instances, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        car = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(car=car, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_rating(self, request, pk=None):
        car = self.get_object()
        try:
            rating = Rating.objects.get(car=car, user=request.user)
            serializer = RatingSerializer(rating, data=request.data)
        except Rating.DoesNotExist:
            serializer = RatingSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(car=car, user=request.user)
            # Update average rating
            avg_rating = car.ratings.aggregate(Avg('rating'))['rating__avg']
            return Response({
                'rating': serializer.data,
                'average_rating': avg_rating
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def available(self, request):
        available_cars = self.queryset.filter(available=True)
        serializer = self.get_serializer(available_cars, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_cars(self, request):
        my_cars = self.queryset.filter(owner=request.user)
        serializer = self.get_serializer(my_cars, many=True)
        return Response(serializer.data)
