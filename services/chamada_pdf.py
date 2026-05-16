"""
Geração do PDF da chamada por ala (A4, compacto para impressão P&B frente/verso).

Impressão duplex: cada ala (exceto a primeira) começa em **página ímpar** (frente da folha).
Se, após o ``PageBreak`` entre alas, a página atual for par, insere-se uma folha em branco
(``_EnsureOddPageStart``) antes do cabeçalho da ala.

Tabela por ala: cabeçalho só no início da ala (sem ``repeatRows``).
Coluna Qtd fora do ``GRID``; ``BOX`` só na célula com número.
Grade em Item–Observações; borda esquerda **externa** da tabela só nas linhas com Qtd preenchida
(``LINEBEFORE`` (0,r) branco nas vazias, **após** o ``BOX`` externo).
A linha à esquerda da coluna Item (grade) permanece em todas as linhas.
Células Qtd vazias: ``LINEBEFORE`` branco; ``LINEABOVE``/``LINEBELOW`` branco só entre duas Qtd
vazias (não apagar topo/fundo do ``BOX`` da linha com número). ``BOX`` da Qtd aplicado por último.
"""

from __future__ import annotations

import unicodedata
from collections import defaultdict
from datetime import datetime
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.flowables import NullDraw

from config.excel_config_control import calculate_shift
from config.units_config import UNITS_CONFIG

UNIT_KEY = "PAMC"
BLOCK_ORDER = {"A": 0, "B": 1}

INSTITUTION_NAME = "Penitenciária Agrícola do Monte Cristo"
CHAMADA_SUBTITLE = "Chamada Nominal"

_WEEKDAYS_PT = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)
_MONTHS_PT = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


def _format_emitido_completo(dt: datetime) -> str:
    """Ex.: Quarta-feira, 13 de maio de 2026 - Plantão ALFA"""
    dia_semana = _WEEKDAYS_PT[dt.weekday()].capitalize()
    mes = _MONTHS_PT[dt.month - 1]
    shift = calculate_shift(dt)
    plantao = f"Plantão {str(shift).upper()}" if shift else "Plantão"
    return f"{dia_semana}, {dt.day} de {mes} de {dt.year} - {plantao}"


def _sort_ala_key(ala_id: str) -> tuple:
    try:
        return (0, int(ala_id))
    except (TypeError, ValueError):
        return (1, str(ala_id or ""))


def _sort_cell_key(cela: str) -> tuple:
    try:
        return (0, int(str(cela).strip()))
    except (TypeError, ValueError):
        return (1, str(cela or "").lower())


def _sort_name_key(nome: str) -> str:
    s = unicodedata.normalize("NFD", nome or "")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower()


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


def _sort_selected_wings(selected: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    """Ordena (Bloco, Ala) para impressão: A antes de B, alas numéricas antes de texto."""

    def wing_key(t: tuple[str, str]) -> tuple:
        b, a = t
        return (BLOCK_ORDER.get(b, 99), b, _sort_ala_key(a))

    return sorted(set(selected), key=wing_key)


class _EnsureOddPageStart(NullDraw):
    """
    Flowable invisível: após ``PageBreak`` entre alas, garante início em página ímpar.

    Em frente/verso, a frente da folha é ímpar (1, 3, 5…). Se a página atual for par,
    agenda um ``FrameBreak`` (folha em branco) antes do conteúdo da próxima ala.
    """

    def wrap(self, availWidth, availHeight):
        if self.canv.getPageNumber() % 2 == 0:
            from reportlab.platypus.doctemplate import FrameBreak

            self._frame.add_generated_content(FrameBreak)
        return (0, 0)


def _ala_section_title(bloco: str, ala_id: str) -> str:
    try:
        name = UNITS_CONFIG[UNIT_KEY]["blocks"][bloco]["alas"][ala_id]["name"]
        block_name = UNITS_CONFIG[UNIT_KEY]["blocks"][bloco].get("name") or f"Bloco {bloco}"
        return f"{block_name} — {name}"
    except (KeyError, TypeError):
        return f"Bloco {bloco} — Ala {ala_id}"


def build_chamada_pdf(
    output_path: str,
    records: list[dict],
    selected_wings: set[tuple[str, str]],
    *,
    unit_label: str = "PAMC",
    generated_at: datetime | None = None,
) -> int:
    """
    Monta o PDF da chamada e grava em ``output_path``.

    ``records`` devem ser dicionários mapeados (Bloco, Ala, Cela, Preso, ...).
    Apenas presos cuja tupla (Bloco, Ala) está em ``selected_wings`` entram.
    O parâmetro ``unit_label`` é mantido por compatibilidade e não altera o PDF.
    Colunas da tabela: **Qtd** (só número na 1ª linha de cada cela), Item, Cela, Nome, Observações.
    Cabeçalho **uma vez por ala**. Qtd fora do ``GRID``; célula com número recebe ``BOX``; Qtd vazia sem bordas.
    Nas linhas com Qtd vazia, apaga-se só a borda esquerda **externa** da célula (0,r); a coluna Item mantém ``LINEBEFORE`` da grade.
    Para impressão frente/verso, cada ala (a partir da 2ª) inicia em página ímpar; página par extra fica em branco.

    Returns:
        Número de alas com pelo menos um preso no PDF.
    Raises:
        ValueError: se não houver nenhum preso nas alas selecionadas após o filtro.
    """
    _ = unit_label

    if not selected_wings:
        raise ValueError("Nenhuma ala selecionada.")

    generated_at = generated_at or datetime.now()
    emitido_texto = _format_emitido_completo(generated_at)

    filtered = [
        r
        for r in records
        if (r.get("Bloco"), r.get("Ala")) in selected_wings
    ]

    wings_order = _sort_selected_wings(selected_wings)
    wings_with_data: list[tuple[str, str]] = []
    for w in wings_order:
        if any((r.get("Bloco"), r.get("Ala")) == w for r in filtered):
            wings_with_data.append(w)

    if not wings_with_data:
        raise ValueError("Nenhum preso mapeado nas alas selecionadas.")

    margin = 12 * mm
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title="Chamada",
    )
    usable_w = A4[0] - 2 * margin

    styles = getSampleStyleSheet()
    inst_style = ParagraphStyle(
        "Institution",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    chamada_nominal_style = ParagraphStyle(
        "ChamadaNominal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "ChamadaMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.grey,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
    wing_header_style = ParagraphStyle(
        "WingHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    name_cell_style = ParagraphStyle(
        "NameInTable",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=9,
    )
    obs_cell_style = ParagraphStyle(
        "ObsInTable",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=9,
    )

    story: list = []
    col_qtd = 18
    col_item = 22
    col_cela = 34
    rest = usable_w - col_qtd - col_item - col_cela
    col_name = rest * 0.56
    col_obs = rest - col_name
    col_widths = [col_qtd, col_item, col_cela, col_name, col_obs]

    for wi, wing in enumerate(wings_with_data):
        if wi > 0:
            story.append(PageBreak())
            story.append(_EnsureOddPageStart())

        bloco, ala_id = wing
        story.append(Paragraph(_escape_xml(INSTITUTION_NAME), inst_style))
        story.append(Paragraph(_escape_xml(CHAMADA_SUBTITLE), chamada_nominal_style))
        story.append(Paragraph(_escape_xml(f"Emitido em: {emitido_texto}"), meta_style))
        story.append(Paragraph(_escape_xml(_ala_section_title(bloco, ala_id)), wing_header_style))

        wing_rows = [r for r in filtered if (r.get("Bloco"), r.get("Ala")) == wing]
        by_cell: dict[str, list[dict]] = defaultdict(list)
        for r in wing_rows:
            by_cell[str(r.get("Cela", "")).strip()].append(r)

        cells_sorted = sorted(by_cell.keys(), key=_sort_cell_key)
        item_no = 1

        # Ordem: Qtd | Item | Cela | Nome | Obs — quantidade só na linha do 1º preso da cela
        table_data: list[list] = [
            ["", "Item", "Cela", "Nome", "Observações"],
        ]

        for cela in cells_sorted:
            inmates = sorted(by_cell[cela], key=lambda x: _sort_name_key(x.get("Preso", "")))
            n = len(inmates)
            for idx, r in enumerate(inmates):
                nome = r.get("Preso", "")
                qtd_val = str(n) if idx == 0 else ""
                table_data.append(
                    [
                        qtd_val,
                        str(item_no),
                        str(cela),
                        Paragraph(_escape_xml(nome), name_cell_style),
                        Paragraph("", obs_cell_style),
                    ]
                )
                item_no += 1

        t = Table(
            table_data,
            colWidths=col_widths,
        )

        def _qtd_cell_is_empty(cell) -> bool:
            if isinstance(cell, str):
                return cell.strip() == ""
            return True

        table_style_cmds: list = [
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("ALIGN", (0, 1), (0, -1), "CENTER"),
            ("ALIGN", (1, 1), (2, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (1, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.white]),
            ("BACKGROUND", (0, 0), (0, -1), colors.white),
            ("BACKGROUND", (1, 0), (-1, 0), colors.HexColor("#CCCCCC")),
            # Grade só Item…Obs: evita linhas horizontais/verticais “vazando” na coluna Qtd
            ("GRID", (1, 0), (4, -1), 0.25, colors.black),
            ("MINIMUMHEIGHT", (4, 1), (4, -1), 20),
        ]

        n_rows = len(table_data)
        table_style_cmds.append(("LINEBELOW", (1, 0), (-1, 0), 0.75, colors.black))
        table_style_cmds.append(("BOX", (0, 0), (-1, -1), 0.5, colors.black))
        # Qtd vazia: sem borda esquerda externa; horizontais brancos só entre duas Qtd vazias
        # (evita apagar topo/fundo do BOX da célula com número).
        for r in range(n_rows):
            if not _qtd_cell_is_empty(table_data[r][0]):
                continue
            table_style_cmds.append(("LINEBEFORE", (0, r), (0, r), 0, colors.white))
            prev_empty = r == 0 or _qtd_cell_is_empty(table_data[r - 1][0])
            if r > 0 and prev_empty:
                table_style_cmds.append(("LINEABOVE", (0, r), (0, r), 0, colors.white))
            next_empty = r == n_rows - 1 or _qtd_cell_is_empty(table_data[r + 1][0])
            if next_empty:
                table_style_cmds.append(("LINEBELOW", (0, r), (0, r), 0, colors.white))
        # Canto superior esquerdo da célula título da Qtd
        table_style_cmds.append(("LINEABOVE", (0, 0), (0, 0), 0, colors.white))

        # BOX na célula com Qtd por último: garante quadradinho fechado após os brancos condicionais
        for r in range(n_rows):
            if not _qtd_cell_is_empty(table_data[r][0]):
                table_style_cmds.append(("BOX", (0, r), (0, r), 0.25, colors.black))
                if r >= 1:
                    table_style_cmds.extend(
                        [
                            ("FONTNAME", (0, r), (0, r), "Helvetica-Bold"),
                            ("FONTSIZE", (0, r), (0, r), 8),
                            ("TEXTCOLOR", (0, r), (0, r), colors.black),
                        ]
                    )

        t.setStyle(TableStyle(table_style_cmds))
        story.append(t)

    doc.build(story)
    return len(wings_with_data)
