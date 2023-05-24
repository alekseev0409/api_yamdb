from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import TokenSerializer, UserSerializer, SignUpSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .utils import create_token, new_code, send_message
from rest_framework import (viewsets, filters, permissions, filters,)
from .permissions import IsOwnerOrReader, IsAdmin
from rest_framework.pagination import LimitOffsetPagination

User = get_user_model()

class TokenView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TokenSerializer
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User,
            username=serializer.validated_data['username']
        )
            response = create_token(user)
            return Response(response)
        

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    pagination_class = LimitOffsetPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated, IsOwnerOrReader],
    )

    def get_my_profile(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(self.request.user)
            return Response(serializer.data)
        serializer = self.get_serializer(
            self.request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=self.request.user.role)
        return Response(serializer.data)
    

class SignUpView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        name = serializer.validated_data['username']
        confirmation_code = new_code()
        send_message(name, confirmation_code, email)
        serializer.save(confirmation_code=confirmation_code)
        return Response(serializer.data)
    

    