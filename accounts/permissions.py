from rest_framework.permissions import BasePermission

class IsAdminOrCoach(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role in ("ADMIN", "COACH"))