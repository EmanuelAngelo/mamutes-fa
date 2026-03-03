from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Iterable, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Play


BASE_W = 500
BASE_H = 700


@dataclass
class PdfRenderOptions:
    title: str = "Playbook"
    author: str = "Mamutes F.A."


def _safe_str(v) -> str:
    return str(v) if v is not None else ""


def _parse_color(value: Optional[str]) -> colors.Color:
    v = (_safe_str(value)).strip()
    if not v:
        return colors.HexColor("#FFC107")  # warning-ish

    lower = v.lower()
    if lower.startswith("#") and len(lower) in (4, 7):
        try:
            return colors.HexColor(lower)
        except Exception:
            return colors.black

    if lower.startswith("rgb(") and lower.endswith(")"):
        try:
            inner = lower[4:-1]
            parts = [p.strip() for p in inner.split(",")]
            r, g, b = [max(0, min(255, int(float(x)))) for x in parts[:3]]
            return colors.Color(r / 255.0, g / 255.0, b / 255.0)
        except Exception:
            return colors.black

    token_map = {
        "warning": colors.HexColor("#FFC107"),
        "error": colors.HexColor("#EF5350"),
        "info": colors.HexColor("#42A5F5"),
        "success": colors.HexColor("#66BB6A"),
        "primary": colors.HexColor("#7E57C2"),
        "secondary": colors.HexColor("#26A69A"),
        "white": colors.white,
        "black": colors.black,
    }
    return token_map.get(lower, colors.HexColor("#FFC107"))


def _draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    font_name: str,
    font_size: float,
    leading: Optional[float] = None,
    max_lines: Optional[int] = None,
):
    if leading is None:
        leading = font_size * 1.25

    words = (text or "").split()
    lines: list[str] = []
    current: list[str] = []

    def flush():
        if current:
            lines.append(" ".join(current))
            current.clear()

    for w in words:
        trial = " ".join([*current, w])
        if c.stringWidth(trial, font_name, font_size) <= max_width:
            current.append(w)
        else:
            flush()
            current.append(w)
    flush()

    if max_lines is not None:
        lines = lines[: max_lines]

    c.setFont(font_name, font_size)
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)


def _draw_field(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    players: list[dict],
    routes: list[dict],
):
    # Field background
    c.saveState()
    c.setFillColor(colors.HexColor("#2E7D32"))
    c.setStrokeColor(colors.HexColor("#1B5E20"))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)

    # Yard lines
    c.setStrokeColor(colors.Color(1, 1, 1, alpha=0.25))
    c.setLineWidth(2)
    for yy in [70, 150, 230, 310, 390, 470, 550, 630]:
        ly = y + (yy / BASE_H) * h
        c.line(x, ly, x + w, ly)

    # Routes first
    for r in routes or []:
        pts = r.get("points") if isinstance(r, dict) else None
        if not isinstance(pts, list) or len(pts) < 2:
            continue

        stroke = _parse_color(_safe_str(r.get("color")))
        c.setStrokeColor(stroke)
        c.setLineWidth(2.5)
        if _safe_str(r.get("type")).lower() == "block":
            c.setDash(6, 4)
        else:
            c.setDash()

        mapped = []
        for p in pts:
            if not isinstance(p, dict):
                continue
            px = float(p.get("x") or 0)
            py = float(p.get("y") or 0)
            mapped.append((x + (px / BASE_W) * w, y + (py / BASE_H) * h))

        if len(mapped) < 2:
            continue

        p0 = mapped[0]
        path = c.beginPath()
        path.moveTo(p0[0], p0[1])
        for (px, py) in mapped[1:]:
            path.lineTo(px, py)
        c.drawPath(path, stroke=1, fill=0)
        c.setDash()

        # Arrow head
        (x1, y1) = mapped[-2]
        (x2, y2) = mapped[-1]
        dx = x2 - x1
        dy = y2 - y1
        if abs(dx) + abs(dy) > 1e-6:
            import math

            angle = math.atan2(dy, dx)
            length = 10
            spread = 0.55
            ax1 = x2 - length * math.cos(angle - spread)
            ay1 = y2 - length * math.sin(angle - spread)
            ax2 = x2 - length * math.cos(angle + spread)
            ay2 = y2 - length * math.sin(angle + spread)

            c.setFillColor(stroke)
            p = c.beginPath()
            p.moveTo(x2, y2)
            p.lineTo(ax1, ay1)
            p.lineTo(ax2, ay2)
            p.close()
            c.drawPath(p, stroke=0, fill=1)

    # Players
    for pl in players or []:
        if not isinstance(pl, dict):
            continue
        px = float(pl.get("x") or 0)
        py = float(pl.get("y") or 0)
        team = _safe_str(pl.get("team")).lower()
        fill = colors.HexColor("#42A5F5") if team != "defense" else colors.HexColor("#EF5350")

        cx = x + (px / BASE_W) * w
        cy = y + (py / BASE_H) * h
        r = 10
        c.setFillColor(fill)
        c.setStrokeColor(colors.white)
        c.setLineWidth(2)
        c.circle(cx, cy, r, stroke=1, fill=1)

        label = _safe_str(pl.get("label")).strip() or _safe_str(pl.get("role")).strip()
        if not label:
            label = _safe_str(pl.get("id"))
        label = label[:3].upper()

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(cx, cy - 3, label)

    c.restoreState()


def render_playbook_pdf(plays: Iterable[Play], opts: Optional[PdfRenderOptions] = None) -> bytes:
    opts = opts or PdfRenderOptions()

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setAuthor(opts.author)
    c.setTitle(opts.title)

    width, height = A4

    def category_sort_key(p: Play) -> str:
        cat = (p.category or "").strip().lower()
        # Attack first, then defense, then blank
        if cat == "ataque":
            return "0"
        if cat == "defesa":
            return "1"
        return "2"

    sorted_plays = sorted(list(plays), key=lambda p: (category_sort_key(p), (p.name or "").lower(), -p.id))

    if not sorted_plays:
        c.setFont("Helvetica-Bold", 18)
        c.drawString(20 * mm, height - 25 * mm, "Playbook vazio")
        c.setFont("Helvetica", 11)
        c.drawString(20 * mm, height - 35 * mm, "Nenhuma jogada cadastrada.")
        c.showPage()
        c.save()
        return buf.getvalue()

    for p in sorted_plays:
        margin_x = 16 * mm
        top = height - 16 * mm

        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin_x, top, _safe_str(p.name))

        meta_y = top - 7 * mm
        c.setFont("Helvetica", 10)
        parts: list[str] = []
        if p.category:
            parts.append(_safe_str(p.category))
        if p.play_type:
            parts.append(f"Tipo: {_safe_str(p.play_type)}")
        if p.formation:
            parts.append(f"Formação: {_safe_str(p.formation)}")
        if parts:
            c.setFillColor(colors.black)
            c.drawString(margin_x, meta_y, " • ".join(parts))

        # Tags
        tags = p.tags if isinstance(p.tags, list) else []
        if tags:
            tag_text = ", ".join([_safe_str(t) for t in tags if _safe_str(t).strip()])
            if tag_text:
                c.setFont("Helvetica", 9)
                c.setFillColor(colors.grey)
                _draw_wrapped_text(c, f"Tags: {tag_text}", margin_x, meta_y - 6 * mm, width - 2 * margin_x, "Helvetica", 9, max_lines=2)

        # Diagram box
        box_w = 120 * mm
        box_h = box_w * (BASE_H / BASE_W)
        box_x = margin_x
        box_y = 30 * mm
        if box_y + box_h > height - 55 * mm:
            box_h = height - 55 * mm - box_y
            box_w = box_h * (BASE_W / BASE_H)

        players = p.players if isinstance(p.players, list) else []
        routes = p.routes if isinstance(p.routes, list) else []
        _draw_field(c, box_x, box_y, box_w, box_h, players=players, routes=routes)

        # Description
        desc_x = box_x + box_w + 10 * mm
        desc_w = width - desc_x - margin_x
        desc_top = top - 18 * mm
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(desc_x, desc_top, "Descrição")

        c.setFont("Helvetica", 10)
        desc = _safe_str(p.description).strip() or "Sem descrição"
        _draw_wrapped_text(c, desc, desc_x, desc_top - 6 * mm, desc_w, "Helvetica", 10, max_lines=18)

        # Footer
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        c.drawRightString(width - margin_x, 10 * mm, "Gerado pelo Mamutes F.A.")

        c.showPage()

    c.save()
    return buf.getvalue()
