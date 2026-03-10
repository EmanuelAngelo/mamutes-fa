from django.db.models import Count, Exists, OuterRef, Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsAdminOrCoach
from .models import Notice, NoticeComment, NoticeLike
from .serializers import (
    NoticeCommentCreateSerializer,
    NoticeCommentSerializer,
    NoticeCreateSerializer,
    NoticeSerializer,
)


class NoticeViewSet(ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAuthenticated]

    search_fields = ("title", "body")
    ordering_fields = ("created_at", "updated_at")

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrCoach()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        like_exists = NoticeLike.objects.filter(notice=OuterRef("pk"), user=user)

        recent_comments_qs = (
            NoticeComment.objects.select_related("user").order_by("-created_at")
        )

        qs = (
            Notice.objects.all()
            .select_related("created_by")
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
                liked_by_me=Exists(like_exists),
            )
            .prefetch_related(
                Prefetch("comments", queryset=recent_comments_qs, to_attr="_recent_comments"),
            )
        )
        return qs

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return NoticeCreateSerializer
        return NoticeSerializer

    def _with_recent_comments(self, items):
        for n in items:
            # `_recent_comments` is newest-first; return up to 3 in oldest-first order.
            recent = list(getattr(n, "_recent_comments", [])[:3])
            recent.reverse()
            setattr(n, "recent_comments", recent)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        items = page if page is not None else qs
        self._with_recent_comments(items)

        serializer = NoticeSerializer(items, many=True, context={"request": request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        notice: Notice = self.get_object()
        self._with_recent_comments([notice])
        serializer = NoticeSerializer(notice, context={"request": request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        create_ser = NoticeCreateSerializer(data=request.data)
        create_ser.is_valid(raise_exception=True)
        notice = Notice.objects.create(
            title=(create_ser.validated_data.get("title") or "").strip(),
            body=create_ser.validated_data["body"],
            created_by=request.user,
        )
        # Re-fetch through annotated queryset so counts/liked_by_me are present.
        notice = self.get_queryset().get(pk=notice.pk)
        self._with_recent_comments([notice])
        out = NoticeSerializer(notice, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk=None):
        notice: Notice = self.get_object()
        obj, created = NoticeLike.objects.get_or_create(notice=notice, user=request.user)
        if not created:
            obj.delete()
            liked = False
        else:
            liked = True

        likes_count = NoticeLike.objects.filter(notice=notice).count()
        return Response({"liked": liked, "likes_count": likes_count})

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        notice: Notice = self.get_object()

        if request.method == "GET":
            qs = NoticeComment.objects.filter(notice=notice).select_related("user").order_by("created_at")
            serializer = NoticeCommentSerializer(qs, many=True)
            return Response(serializer.data)

        create_ser = NoticeCommentCreateSerializer(data=request.data)
        create_ser.is_valid(raise_exception=True)
        c = NoticeComment.objects.create(
            notice=notice,
            user=request.user,
            text=create_ser.validated_data["text"],
        )
        out = NoticeCommentSerializer(c)
        comments_count = NoticeComment.objects.filter(notice=notice).count()
        return Response({"comment": out.data, "comments_count": comments_count}, status=status.HTTP_201_CREATED)
