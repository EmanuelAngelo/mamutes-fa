from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django.http import HttpResponse

from accounts.permissions import IsAdminOrCoachOrReadOnly
from .models import Play
from .serializers import PlaySerializer
from .pdf import render_playbook_pdf


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all().order_by("-created_at")
    serializer_class = PlaySerializer
    permission_classes = [IsAdminOrCoachOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    search_fields = ("name", "description", "category")
    ordering_fields = ("created_at", "updated_at", "name")

    @action(detail=False, methods=["get"], url_path="export/pdf")
    def export_pdf(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        pdf_bytes = render_playbook_pdf(qs, opts=None)
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="playbook.pdf"'
        return resp

    @action(detail=True, methods=["get"], url_path="export/pdf")
    def export_play_pdf(self, request, *args, **kwargs):
        play = self.get_object()
        pdf_bytes = render_playbook_pdf([play], opts=None)
        safe_name = (play.name or "jogada").strip().replace('"', "") or "jogada"
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = f'attachment; filename="{safe_name}.pdf"'
        return resp

    @action(detail=True, methods=["post"], url_path="clone")
    def clone(self, request, *args, **kwargs):
        src: Play = self.get_object()

        base_name = (src.name or "").strip() or "Jogada"
        suffix = " (cópia)"
        name = (base_name + suffix)[: Play._meta.get_field("name").max_length]

        clone = Play.objects.create(
            name=name,
            description=src.description,
            formation=src.formation,
            play_type=src.play_type,
            tags=list(src.tags or []),
            players=list(src.players or []),
            routes=list(src.routes or []),
            category=src.category,
            image=None,
        )

        serializer = self.get_serializer(clone)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
