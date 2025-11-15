from datetime import datetime, timedelta
from collections import defaultdict
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from database.config import get_db
from entities.paquete import Paquete
from entities.detalle_entrega import DetalleEntrega
from entities.sede import Sede
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/analytics", tags=["Analitica"]) 


@router.get("/paquetes-ultimos-30-dias")
def paquetes_ultimos_30_dias(days: int = 30, db: Session = Depends(get_db)):
    days = max(1, min(365, int(days)))
    start_date = datetime.now() - timedelta(days=days - 1)
    q = (
        db.query(
            cast(Paquete.fecha_creacion, Date).label("d"),
            func.count(Paquete.id_paquete),
        )
        .filter(Paquete.fecha_creacion >= start_date)
        .group_by("d")
        .order_by("d")
    )
    rows = q.all()
    counts_by_date = {r[0]: r[1] for r in rows}
    labels = []
    data = []
    for i in range(days):
        d = (start_date.date() + timedelta(days=i))
        labels.append(d.isoformat())
        data.append(int(counts_by_date.get(d, 0)))
    return {"labels": labels, "data": data}


@router.get("/sedes-mas-activas")
def sedes_mas_activas(limit: int = 5, days: int = 90, db: Session = Depends(get_db)):
    days = max(1, min(365, int(days)))
    start_date = datetime.now() - timedelta(days=days - 1)
    remitente_counts = dict(
        db.query(
            DetalleEntrega.id_sede_remitente, func.count(DetalleEntrega.id_detalle)
        )
        .filter(DetalleEntrega.fecha_envio >= start_date)
        .group_by(DetalleEntrega.id_sede_remitente)
        .all()
    )
    receptora_counts = dict(
        db.query(
            DetalleEntrega.id_sede_receptora, func.count(DetalleEntrega.id_detalle)
        )
        .filter(DetalleEntrega.fecha_envio >= start_date)
        .group_by(DetalleEntrega.id_sede_receptora)
        .all()
    )
    total_counts = defaultdict(int)
    for k, v in remitente_counts.items():
        total_counts[k] += v
    for k, v in receptora_counts.items():
        total_counts[k] += v
    if not total_counts:
        return {"labels": [], "data": []}
    sedes = (
        db.query(Sede.id_sede, Sede.nombre)
        .filter(Sede.id_sede.in_(list(total_counts.keys())))
        .all()
    )
    name_map = {sid: name for sid, name in sedes}
    items = []
    for sid, count in total_counts.items():
        name = name_map.get(sid, str(sid))
        items.append((name, int(count)))
    items.sort(key=lambda x: x[1], reverse=True)
    items = items[: max(1, int(limit))]
    labels = [i[0] for i in items]
    data = [i[1] for i in items]
    return {"labels": labels, "data": data}


@router.get("/estados-paquetes")
def estados_paquetes(days: int = 90, db: Session = Depends(get_db)):
    days = max(1, min(365, int(days)))
    start_date = datetime.now() - timedelta(days=days - 1)
    rows = (
        db.query(Paquete.estado, func.count(Paquete.id_paquete))
        .filter(Paquete.fecha_creacion >= start_date)
        .group_by(Paquete.estado)
        .all()
    )
    labels = [r[0] for r in rows]
    data = [int(r[1]) for r in rows]
    return {"labels": labels, "data": data}


@router.get("/tiempo-promedio-entrega")
def tiempo_promedio_entrega(days: int = 180, db: Session = Depends(get_db)):
    days = max(1, min(365, int(days)))
    start_date = datetime.now() - timedelta(days=days - 1)
    avg_seconds = db.query(
        func.avg(
            func.extract(
                "epoch", DetalleEntrega.fecha_entrega - DetalleEntrega.fecha_envio
            )
        )
    ).filter(DetalleEntrega.fecha_entrega.isnot(None), DetalleEntrega.fecha_envio >= start_date).scalar()
    if avg_seconds is None:
        return {"avg_hours": 0.0, "avg_days": 0.0}
    avg_hours = float(avg_seconds) / 3600.0
    avg_days = avg_hours / 24.0
    return {"avg_hours": round(avg_hours, 2), "avg_days": round(avg_days, 2)}


@router.get("/resumen")
def resumen(db: Session = Depends(get_db)):
    total_paquetes = db.query(func.count(Paquete.id_paquete)).scalar() or 0
    start_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    paquetes_mes = (
        db.query(func.count(Paquete.id_paquete))
        .filter(Paquete.fecha_creacion >= start_month)
        .scalar()
        or 0
    )
    sedes_activas = db.query(func.count(Sede.id_sede)).filter(Sede.activo == True).scalar() or 0
    entregas_pendientes = (
        db.query(func.count(DetalleEntrega.id_detalle))
        .filter(DetalleEntrega.estado_envio != "Entregado")
        .scalar()
        or 0
    )
    return {
        "total_paquetes": int(total_paquetes),
        "paquetes_mes": int(paquetes_mes),
        "sedes_activas": int(sedes_activas),
        "entregas_pendientes": int(entregas_pendientes),
    }


@router.get("/export-resumen")
def export_resumen(
    days_line: int = 30,
    days_states: int = 90,
    days_top: int = 90,
    top_limit: int = 5,
    db: Session = Depends(get_db),
):
    days_line = max(1, min(365, int(days_line)))
    days_states = max(1, min(365, int(days_states)))
    days_top = max(1, min(365, int(days_top)))
    top_limit = max(1, min(50, int(top_limit)))

    resumen_data = resumen(db)
    ultimos30 = paquetes_ultimos_30_dias(days_line, db)
    sedes_top = sedes_mas_activas(top_limit, days_top, db)
    estados = estados_paquetes(days_states, db)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Reporte de analítica SwiftPost")
    y -= 30

    pdf.setFont("Helvetica", 12)
    pdf.drawString(
        50, y, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    y -= 30

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Resumen")
    y -= 20
    pdf.setFont("Helvetica", 12)
    pdf.drawString(60, y, f"Total de paquetes: {resumen_data['total_paquetes']}")
    y -= 16
    pdf.drawString(60, y, f"Paquetes este mes: {resumen_data['paquetes_mes']}")
    y -= 16
    pdf.drawString(60, y, f"Sedes activas: {resumen_data['sedes_activas']}")
    y -= 16
    pdf.drawString(
        60, y, f"Entregas pendientes: {resumen_data['entregas_pendientes']}"
    )
    y -= 30

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Sedes más activas")
    y -= 20
    pdf.setFont("Helvetica", 12)
    for label, value in zip(sedes_top["labels"], sedes_top["data"]):
        pdf.drawString(60, y, f"{label}: {int(value)} envíos")
        y -= 16
        if y < 80:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 12)

    if y < 140:
        pdf.showPage()
        y = height - 50

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Estados de paquetes")
    y -= 20
    pdf.setFont("Helvetica", 12)
    for label, value in zip(estados["labels"], estados["data"]):
        pdf.drawString(60, y, f"{label}: {int(value)}")
        y -= 16
        if y < 80:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 12)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    filename = f"reporte_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
