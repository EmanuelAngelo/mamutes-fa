from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsAdminOrCoach(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, "profile", None)
        return bool(profile and profile.role in ("ADMIN", "COACH"))


class IsAdminOrCoachOrReadOnly(BasePermission):
    """Allow any authenticated user to read; only Admin/Coach can write."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return IsAdminOrCoach().has_permission(request, view)