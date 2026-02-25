from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from rest_framework.generics import ListCreateAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.permissions import IsAdminOrCoach
from .serializers import MeSerializer, ChangePasswordSerializer, UserListSerializer, UserCreateSerializer


class UsersView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrCoach]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email", "id"]
    ordering = ["username"]

    def get_queryset(self):
        qs = (
            User.objects.all()
            .select_related("profile")
            .order_by("username")
        )

        unlinked = self.request.query_params.get("unlinked")
        include = self.request.query_params.get("include")

        # Default: only users without an athlete linked.
        if unlinked is None or unlinked in ("1", "true", "True"):
            base = qs.filter(athlete__isnull=True)
        else:
            base = qs

        if include:
            try:
                include_id = int(include)
                base = (base | qs.filter(id=include_id)).distinct()
            except (TypeError, ValueError):
                pass

        return base.order_by("username")

    def get_serializer_class(self):
        if self.request.method.upper() == "POST":
            return UserCreateSerializer
        return UserListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserListSerializer(user).data, status=status.HTTP_201_CREATED)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(MeSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(current_password):
            return Response({"current_password": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response({"detail": "Password updated."})