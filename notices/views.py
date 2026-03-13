import logging
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Profile
from accounts.permissions import IsAdminOrCoach
from .models import Notice, NoticeComment, NoticeLike, PushSubscription
from .serializers import (
    NoticeCommentCreateSerializer,
    NoticeCommentSerializer,
    NoticeCreateSerializer,
    NoticeSerializer,
    PushSubscriptionSerializer,
    PushSubscriptionUnsubscribeSerializer,
    PushSubscriptionUpsertSerializer,
)

logger = logging.getLogger(__name__)
User = get_user_model()


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
            .order_by("-pinned", "-created_at")
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

        self._send_notice_push(notice)

        out = NoticeSerializer(notice, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    def _send_notice_push(self, notice: Notice) -> None:
        public_key = (getattr(settings, "WEBPUSH_VAPID_PUBLIC_KEY", "") or "").strip()
        private_key = (getattr(settings, "WEBPUSH_VAPID_PRIVATE_KEY", "") or "").strip()
        subject = (getattr(settings, "WEBPUSH_VAPID_SUBJECT", "") or "").strip()
        if not public_key or not private_key or not subject:
            return

        if "BEGIN PRIVATE KEY" not in private_key and "BEGIN EC PRIVATE KEY" not in private_key:
            p = Path(private_key)
            if p.is_file():
                try:
                    private_key = p.read_text(encoding="utf-8").strip()
                except Exception:
                    logger.exception("Falha ao ler WEBPUSH_VAPID_PRIVATE_KEY de arquivo")
                    return

        try:
            import importlib

            pywebpush = importlib.import_module("pywebpush")
            webpush = getattr(pywebpush, "webpush")
            WebPushException = getattr(pywebpush, "WebPushException")
        except Exception:
            logger.exception("pywebpush não está disponível")
            return

        body = (notice.body or "").strip()
        if len(body) > 180:
            body = body[:179] + "…"

        title = (notice.title or "").strip() or "Novo aviso"
        payload = {
            "type": "notice_created",
            "notice_id": notice.pk,
            "title": title,
            "body": body,
            "url": "/notices",
        }

        recipient_users = (
            User.objects.filter(profile__role__in=[Profile.Role.COACH, Profile.Role.PLAYER])
            .exclude(pk=notice.created_by_id)
            .distinct()
        )

        subs = PushSubscription.objects.filter(user__in=recipient_users).select_related("user")
        if not subs.exists():
            return

        claims = {"sub": subject}
        import json as _json

        data = _json.dumps(payload, ensure_ascii=False)

        for sub in subs:
            try:
                webpush(
                    subscription_info=sub.as_webpush_subscription(),
                    data=data,
                    vapid_private_key=private_key,
                    vapid_claims=claims,
                    ttl=60 * 60,
                )
            except WebPushException as exc:
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                if status_code in {404, 410}:
                    sub.delete()
                else:
                    logger.warning("Falha ao enviar push para sub %s (HTTP %s)", sub.pk, status_code)
            except Exception:
                logger.exception("Erro inesperado ao enviar push")

    @action(detail=False, methods=["get"], url_path="push/public-key")
    def push_public_key(self, request):
        return Response({"publicKey": (getattr(settings, "WEBPUSH_VAPID_PUBLIC_KEY", "") or "").strip()})

    @action(detail=False, methods=["get"], url_path="push/subscriptions")
    def push_list_subscriptions(self, request):
        qs = PushSubscription.objects.filter(user=request.user).order_by("-updated_at")
        return Response(PushSubscriptionSerializer(qs, many=True).data)

    @action(detail=False, methods=["post"], url_path="push/subscribe")
    def push_subscribe(self, request):
        public_key = (getattr(settings, "WEBPUSH_VAPID_PUBLIC_KEY", "") or "").strip()
        private_key = (getattr(settings, "WEBPUSH_VAPID_PRIVATE_KEY", "") or "").strip()
        if not public_key or not private_key:
            return Response(
                {"detail": "Web Push não configurado no servidor (VAPID keys ausentes)."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if "BEGIN PRIVATE KEY" not in private_key and "BEGIN EC PRIVATE KEY" not in private_key:
            p = Path(private_key)
            if p.is_file():
                try:
                    private_key = p.read_text(encoding="utf-8").strip()
                except Exception:
                    logger.exception("Falha ao ler WEBPUSH_VAPID_PRIVATE_KEY de arquivo")
                    return Response(
                        {"detail": "Web Push mal configurado no servidor (private key inválida)."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )

        ser = PushSubscriptionUpsertSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        endpoint = ser.validated_data["endpoint"]
        keys = ser.validated_data["keys"]
        user_agent = ser.validated_data.get("user_agent", "")

        obj, _created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                "user": request.user,
                "p256dh": keys["p256dh"],
                "auth": keys["auth"],
                "user_agent": user_agent or "",
            },
        )
        return Response(PushSubscriptionSerializer(obj).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="push/unsubscribe")
    def push_unsubscribe(self, request):
        ser = PushSubscriptionUnsubscribeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        endpoint = ser.validated_data["endpoint"]
        PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
