"""
PDF de contagem por ala/cela: QTD do sistema + coluna PREENCHER para anotação manual.
A4 paisagem; várias alas por linha (grade); cada ala só com linhas de dados = quantidade de celas.
Cabeçalho institucional (penitenciária, título, emitido) repetido em todas as páginas.
Alas sem ``celas`` no config não geram bloco.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config.units_config import UNITS_CONFIG
from services.chamada_pdf import (
    INSTITUTION_NAME,
    _ala_section_title,
    _format_emitido_completo,
    _sort_selected_wings,
)

UNIT_KEY = "PAMC"
SUBTITLE = "Ficha de contagem por cela"

# Quantas alas lado a lado em cada linha da grade (A4 paisagem ~842 pt úteis)
_ALAS_POR_LINHA = 4
# Linha vertical entre alas (tesoura)
_SEPARADOR_ALAS_PT = 2.8

# Linhas da mini-tabela de cada ala
_ROW_TITLE_PT = 11
_ROW_HEADER_PT = 9
_ROW_DATA_PT = 9
_MIN_TITLE = 28
_MIN_HEADER = 18
_MIN_DATA = 17
_CELL_ROW_LEADING_EXTRA = 3

_CELA_BG = colors.HexColor("#b8d4f0")
_HEADER_BG = colors.HexColor("#cccccc")

# Faixa reservada no topo para cabeçalho repetido em todas as páginas
_HEADER_TOP_RESERVE = 22 * mm


def _draw_contagem_header(
    canvas,
    doc,
    *,
    emitido: str,
    inst_style: ParagraphStyle,
    sub_style: ParagraphStyle,
    meta_style: ParagraphStyle,
    rw: float,
    lm: float,
) -> None:
    """Desenha o mesmo cabeçalho institucional acima da área de fluxo (todas as páginas)."""
    canvas.saveState()
    pw, ph = doc.pagesize
    rm = doc.rightMargin
    strip_bottom = ph - doc.topMargin

    # De baixo para cima na faixa: linha → emitido → subtítulo → instituição
    meta_b = strip_bottom + 4
    p_meta = Paragraph(_escape_xml(f"Emitido em: {emitido}"), meta_style)
    _, mh = p_meta.wrap(rw, 120)
    p_meta.drawOn(canvas, lm, meta_b)

    sub_b = meta_b + mh + 5
    p_sub = Paragraph(_escape_xml(SUBTITLE), sub_style)
    sw, sh = p_sub.wrap(rw, 120)
    p_sub.drawOn(canvas, lm + (rw - sw) / 2, sub_b)

    inst_b = sub_b + sh + 5
    p_inst = Paragraph(_escape_xml(INSTITUTION_NAME), inst_style)
    iw, ih = p_inst.wrap(rw, 120)
    p_inst.drawOn(canvas, lm + (rw - iw) / 2, inst_b)

    canvas.setStrokeColorRGB(0, 0, 0)
    canvas.setLineWidth(0.5)
    canvas.line(lm, strip_bottom, pw - rm, strip_bottom)
    canvas.restoreState()


def _escape_xml(text: str) -> str:
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _wings_with_celas(selected_wings: Iterable[tuple[str, str]]) -> list[dict]:
    """Alas selecionadas que possuem lista ``celas`` não vazia no config."""
    pamc = UNITS_CONFIG.get(UNIT_KEY, {})
    blocks = pamc.get("blocks") or {}
    out: list[dict] = []
    for bloco, ala_id in _sort_selected_wings(selected_wings):
        try:
            ala_cfg = blocks[bloco]["alas"][ala_id]
        except (KeyError, TypeError):
            continue
        celas = ala_cfg.get("celas") or []
        if not celas:
            continue
        out.append(
            {
                "bloco": bloco,
                "ala_id": ala_id,
                "celas": list(celas),
            }
        )
    return out


def _aggregate_counts(records: list[dict], selected_wings: set[tuple[str, str]]) -> dict[tuple[str, str, str], int]:
    counts: dict[tuple[str, str, str], int] = defaultdict(int)
    for r in records:
        b = str(r.get("Bloco", "")).strip()
        a = str(r.get("Ala", "")).strip()
        c = str(r.get("Cela", "")).strip()
        if (b, a) not in selected_wings:
            continue
        counts[(b, a, c)] += 1
    return counts


def _paragraph_block_height(p: Paragraph, max_width: float) -> float:
    _, h = p.wrap(max_width, 9999)
    return float(h)


def _wing_table_impl(
    *,
    bloco: str,
    ala_id: str,
    celas: list[str],
    counts: dict[tuple[str, str, str], int],
    col_width: float,
    styles,
    title_text: str,
    title_row_h: float,
    header_row_h: float,
    data_row_h: float,
) -> Table:
    title_style = ParagraphStyle(
        "ContTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=_ROW_TITLE_PT,
        leading=_ROW_TITLE_PT + 1,
        textColor=colors.black,
        alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        "ContSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=8,
        textColor=colors.black,
        alignment=TA_CENTER,
    )
    cell_style = ParagraphStyle(
        "ContCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=_ROW_DATA_PT if data_row_h >= 13 else 7,
        leading=max(6.0, min(data_row_h - 3.0, _ROW_DATA_PT + _CELL_ROW_LEADING_EXTRA)),
        alignment=TA_CENTER,
    )

    title_para = Paragraph(_escape_xml(title_text), title_style)

    data: list[list] = [
        [title_para, "", ""],
        [
            Paragraph(_escape_xml("CELA"), sub_style),
            Paragraph(_escape_xml("QTD"), sub_style),
            Paragraph(_escape_xml("PREENCHER"), sub_style),
        ],
    ]

    for cela in celas:
        q = counts.get((bloco, ala_id, str(cela).strip()), 0)
        data.append(
            [
                Paragraph(_escape_xml(str(cela)), cell_style),
                Paragraph(_escape_xml(str(q)), cell_style),
                Paragraph("", cell_style),
            ]
        )

    # QTD e coluna manual com a mesma largura; Cela ocupa o restante
    side = col_width * 0.30
    cw0 = col_width - 2 * side
    cw1 = side
    cw2 = side

    st = [
        ("SPAN", (0, 0), (2, 0)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 0), (2, 0), _HEADER_BG),
        ("BACKGROUND", (0, 1), (2, 1), _HEADER_BG),
        ("BACKGROUND", (0, 2), (0, -1), _CELA_BG),
        ("BACKGROUND", (1, 2), (1, -1), colors.white),
        ("BACKGROUND", (2, 2), (2, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("TOPPADDING", (0, 0), (-1, 1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, 1), 2),
        ("TOPPADDING", (0, 2), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 2), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
    ]
    row_heights = [title_row_h, header_row_h] + [data_row_h] * len(celas)

    t = Table(data, colWidths=[cw0, cw1, cw2], rowHeights=row_heights, repeatRows=0)
    t.setStyle(TableStyle(st))
    return t


def build_contagem_pdf(
    output_path: str,
    records: list[dict],
    selected_wings: set[tuple[str, str]],
    *,
    unit_label: str = "PAMC",
    generated_at: datetime | None = None,
) -> int:
    """
    Gera PDF de contagem em A4 paisagem.

    Returns:
        Número de blocos (alas) incluídos no PDF.
    Raises:
        ValueError: seleção vazia ou nenhuma ala com celas cadastradas.
    """
    _ = unit_label

    if not selected_wings:
        raise ValueError("Nenhuma ala selecionada.")

    wings = _wings_with_celas(selected_wings)
    if not wings:
        raise ValueError(
            "Nenhuma ala selecionada possui lista de celas no cadastro (alas vazias não entram na contagem)."
        )

    generated_at = generated_at or datetime.now()
    emitido = _format_emitido_completo(generated_at)

    sel_norm = {(str(b), str(a)) for b, a in selected_wings}
    counts = _aggregate_counts(records, sel_norm)

    margin = 10 * mm
    page = landscape(A4)
    _, page_h = page
    # Altura útil aproximada do frame de conteúdo (desconto extra p/ bordas internas do ReportLab)
    frame_body = float(page_h) - float(_HEADER_TOP_RESERVE) - float(margin) - 14.0
    n_max_celas = max(len(w["celas"]) for w in wings)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=page,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=_HEADER_TOP_RESERVE,
        bottomMargin=margin,
        title="Contagem",
    )
    usable_w = page[0] - 2 * margin
    rw_header = usable_w
    lm_header = margin
    cols = _ALAS_POR_LINHA
    col_w = usable_w / cols

    styles = getSampleStyleSheet()

    title_style_m = ParagraphStyle(
        "ContTitleMeas",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=_ROW_TITLE_PT,
        leading=_ROW_TITLE_PT + 1,
        textColor=colors.black,
        alignment=TA_CENTER,
    )
    sub_style_tbl = ParagraphStyle(
        "ContSubMeas",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=8,
        textColor=colors.black,
        alignment=TA_CENTER,
    )
    max_title_h = 0.0
    for w in wings:
        tt = _ala_section_title(w["bloco"], w["ala_id"])
        ph = Paragraph(_escape_xml(tt), title_style_m)
        max_title_h = max(max_title_h, _paragraph_block_height(ph, col_w))
    title_row_h = max(max_title_h + 4.0, 22.0)

    side_m = col_w * 0.30
    cw0m = col_w - 2 * side_m
    cw1m = side_m
    cw2m = side_m
    pp0 = Paragraph(_escape_xml("CELA"), sub_style_tbl)
    pp1 = Paragraph(_escape_xml("QTD"), sub_style_tbl)
    pp2 = Paragraph(_escape_xml("PREENCHER"), sub_style_tbl)
    hdr_h = max(
        _paragraph_block_height(pp0, max(cw0m - 6, 10.0)),
        _paragraph_block_height(pp1, max(cw1m - 6, 10.0)),
        _paragraph_block_height(pp2, max(cw2m - 6, 10.0)),
    )
    header_row_h = max(hdr_h + 4.0, 12.0)

    outer_reserve = 58.0
    data_row_h = (frame_body - outer_reserve - title_row_h - header_row_h) / max(n_max_celas, 1)
    data_row_h = max(8.5, min(15.5, data_row_h))

    inst_style = ParagraphStyle(
        "ContInst",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    sub_style = ParagraphStyle(
        "ContSubDoc",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    meta_style = ParagraphStyle(
        "ContMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.grey,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    def _on_page(canvas, doc):
        _draw_contagem_header(
            canvas,
            doc,
            emitido=emitido,
            inst_style=inst_style,
            sub_style=sub_style,
            meta_style=meta_style,
            rw=rw_header,
            lm=lm_header,
        )

    story: list = []
    wing_tables: list[Table] = []
    for w in wings:
        bloco = w["bloco"]
        ala_id = w["ala_id"]
        celas = w["celas"]
        title_text = _ala_section_title(bloco, ala_id)
        wing_tables.append(
            _wing_table_impl(
                bloco=bloco,
                ala_id=ala_id,
                celas=celas,
                counts=counts,
                col_width=col_w,
                styles=styles,
                title_text=title_text,
                title_row_h=title_row_h,
                header_row_h=header_row_h,
                data_row_h=data_row_h,
            )
        )

    for i in range(0, len(wing_tables), cols):
        row_cells = list(wing_tables[i : i + cols])
        while len(row_cells) < cols:
            row_cells.append(Spacer(col_w, 1))
        grid_row = Table(
            [row_cells],
            colWidths=[col_w] * cols,
            hAlign="CENTER",
        )
        pair_style = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, -1), 0.8, colors.HexColor("#666666")),
        ]
        for c in range(cols - 1):
            pair_style.append(
                ("LINEAFTER", (c, 0), (c, 0), _SEPARADOR_ALAS_PT, colors.black),
            )
        grid_row.setStyle(TableStyle(pair_style))
        story.append(grid_row)

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return len(wing_tables)
