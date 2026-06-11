from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_JUSTIFY
import io
import html

# ─────────────────────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────────────────────
C_NAME    = colors.HexColor("#0D0D0D")
C_HEADING = colors.HexColor("#1A1A2E")
C_ACCENT  = colors.HexColor("#2563EB")
C_BODY    = colors.HexColor("#1F1F1F")
C_MUTED   = colors.HexColor("#4B5563")
C_RULE    = colors.HexColor("#D1D5DB")


# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
def get_styles():
    return {
        "name": ParagraphStyle(
            "name", fontName="Helvetica-Bold", fontSize=22,
            textColor=C_NAME, leading=26, spaceAfter=1, alignment=TA_LEFT,
        ),
        "tagline": ParagraphStyle(
            "tagline", fontName="Helvetica", fontSize=10.5,
            textColor=C_MUTED, leading=14, spaceAfter=4, alignment=TA_LEFT,
        ),
        "contact": ParagraphStyle(
            "contact", fontName="Helvetica", fontSize=8.5,
            textColor=C_MUTED, leading=12, spaceAfter=5, alignment=TA_LEFT,
        ),
        "section": ParagraphStyle(
            "section", fontName="Helvetica-Bold", fontSize=9,
            textColor=C_HEADING, leading=12, spaceBefore=10, spaceAfter=2,
        ),
        "role_title": ParagraphStyle(
            "role_title", fontName="Helvetica-Bold", fontSize=10,
            textColor=C_BODY, leading=14, spaceBefore=6, spaceAfter=0,
        ),
        "meta": ParagraphStyle(
            "meta", fontName="Helvetica-Oblique", fontSize=8.5,
            textColor=C_MUTED, leading=13, spaceAfter=3, alignment=TA_RIGHT,
        ),
        "summary": ParagraphStyle(
            "summary", fontName="Helvetica", fontSize=9.5,
            textColor=C_BODY, leading=15, spaceAfter=4, alignment=TA_JUSTIFY,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=9.5,
            textColor=C_BODY, leading=14, alignment=TA_LEFT,
        ),
        "body_just": ParagraphStyle(
            "body_just", fontName="Helvetica", fontSize=9.5,
            textColor=C_BODY, leading=14, alignment=TA_JUSTIFY,
        ),
        "edu_degree": ParagraphStyle(
            "edu_degree", fontName="Helvetica-Bold", fontSize=10,
            textColor=C_BODY, leading=14, spaceBefore=5, spaceAfter=0,
        ),
        "edu_detail": ParagraphStyle(
            "edu_detail", fontName="Helvetica", fontSize=9,
            textColor=C_MUTED, leading=13, spaceAfter=2,
        ),
    }


# ─────────────────────────────────────────────────────────────
# CORE BULLET BUILDER — using fixed-width Table (100% reliable)
# ─────────────────────────────────────────────────────────────
def _bullet_row(text: str, styles: dict, W: float, justify: bool = True) -> Table:
    """
    Builds ONE bullet line as a 2-column table:
      [ blue dot (10pt wide) ] [ text fills the rest ]

    This GUARANTEES perfect alignment because the dot occupies a fixed
    column width — wrapped text NEVER drifts under the dot.
    """
    safe = html.escape(text)

    dot_style = ParagraphStyle(
        "dot",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=C_ACCENT,
        leading=14,
        alignment=TA_LEFT,
    )

    text_style = styles["body_just"] if justify else styles["body"]

    DOT_W = 10  # fixed width in points
    row = Table(
        [[
            Paragraph("\u2022", dot_style),
            Paragraph(safe, text_style),
        ]],
        colWidths=[DOT_W, W - DOT_W],
    )
    row.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return row


# ─────────────────────────────────────────────────────────────
# SECTION HEADER
# ─────────────────────────────────────────────────────────────
def _section_header(title: str, styles: dict, W: float) -> list:
    return [
        Spacer(1, 4),
        Paragraph(title.upper(), styles["section"]),
        HRFlowable(
            width=W, thickness=0.6, color=C_RULE,
            spaceBefore=1, spaceAfter=4,
        ),
    ]


# ─────────────────────────────────────────────────────────────
# TWO-COLUMN HEADER ROW (title left, date right)
# ─────────────────────────────────────────────────────────────
def _title_date_row(left_text: str, right_text: str, styles: dict, W: float) -> Table:
    t = Table(
        [[
            Paragraph(left_text, styles["role_title"]),
            Paragraph(right_text, styles["meta"]),
        ]],
        colWidths=[W * 0.70, W * 0.30],
    )
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return t


# ─────────────────────────────────────────────────────────────
# MAIN PDF BUILDER
# ─────────────────────────────────────────────────────────────
def build_resume_pdf(resume_data: dict) -> bytes:
    buffer = io.BytesIO()
    styles = get_styles()

    LEFT, RIGHT, TOP, BOTTOM = 16 * mm, 16 * mm, 14 * mm, 14 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOTTOM,
        title=resume_data.get("name", "Resume"),
        author=resume_data.get("name", ""),
        subject=resume_data.get("target_role", "Resume"),
        creator="ResumeIQ",
        allowSplitting=1,   # ← Allow content to flow to multiple pages
    )

    W = A4[0] - LEFT - RIGHT
    story = []

    # ═══════════════════════════════════════════════════════
    # HEADER
    # ═══════════════════════════════════════════════════════
    name     = (resume_data.get("name") or "").strip()
    tagline  = (resume_data.get("target_role") or "").strip()
    email    = (resume_data.get("email") or "").strip()
    phone    = (resume_data.get("phone") or "").strip()
    linkedin = (resume_data.get("linkedin") or "").strip()
    github   = (resume_data.get("github") or "").strip()
    location = (resume_data.get("location") or "").strip()

    if name:
        story.append(Paragraph(html.escape(name), styles["name"]))

    story.append(HRFlowable(
        width=W, thickness=2, color=C_ACCENT,
        spaceBefore=0, spaceAfter=3,
    ))

    if tagline:
        story.append(Paragraph(html.escape(tagline), styles["tagline"]))

    contact_parts = []
    if email:    contact_parts.append(html.escape(email))
    if phone:    contact_parts.append(html.escape(phone))
    if location: contact_parts.append(html.escape(location))
    if linkedin:
        label = linkedin.split("linkedin.com/in/")[-1].rstrip("/") if "linkedin.com" in linkedin else linkedin
        contact_parts.append(f"LinkedIn: {html.escape(label)}")
    if github:
        label = github.split("github.com/")[-1].rstrip("/") if "github.com" in github else github
        contact_parts.append(f"GitHub: {html.escape(label)}")

    if contact_parts:
        story.append(Paragraph("  \u2022  ".join(contact_parts), styles["contact"]))

    story.append(HRFlowable(
        width=W, thickness=0.5, color=C_RULE,
        spaceBefore=2, spaceAfter=0,
    ))

    # ═══════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════
    summary = (resume_data.get("summary") or "").strip()
    if summary:
        story += _section_header("Professional Summary", styles, W)
        story.append(Paragraph(html.escape(summary), styles["summary"]))

    # ═══════════════════════════════════════════════════════
    # SKILLS — 3-column table, perfect alignment
    # ═══════════════════════════════════════════════════════
    skills = [s.strip() for s in (resume_data.get("skills") or []) if s and s.strip()]
    if skills:
        story += _section_header("Technical Skills", styles, W)

        COLS = 3
        # Fill column-by-column (newspaper style)
        n = len(skills)
        rows_count = (n + COLS - 1) // COLS
        # Pad
        while len(skills) < rows_count * COLS:
            skills.append("")

        grid = [["" for _ in range(COLS)] for _ in range(rows_count)]
        for idx, skill in enumerate(skills):
            col = idx // rows_count
            row = idx % rows_count
            if col < COLS:
                grid[row][col] = skill

        col_w = W / COLS
        DOT_W = 9

        table_data = []
        for row in grid:
            cells = []
            for s in row:
                if s:
                    cell = Table(
                        [[
                            Paragraph(
                                "\u2022",
                                ParagraphStyle("d", fontName="Helvetica-Bold",
                                    fontSize=10, textColor=C_ACCENT, leading=14)
                            ),
                            Paragraph(
                                html.escape(s),
                                ParagraphStyle("s", fontName="Helvetica",
                                    fontSize=9.5, textColor=C_BODY, leading=14)
                            ),
                        ]],
                        colWidths=[DOT_W, col_w - DOT_W - 8],
                    )
                    cell.setStyle(TableStyle([
                        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                        ("TOPPADDING",    (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]))
                    cells.append(cell)
                else:
                    cells.append("")
            table_data.append(cells)

        skill_table = Table(table_data, colWidths=[col_w] * COLS)
        skill_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(skill_table)

    # ═══════════════════════════════════════════════════════
    # EXPERIENCE
    # ═══════════════════════════════════════════════════════
    experience = resume_data.get("experience") or []
    if experience:
        story += _section_header("Professional Experience", styles, W)

        for exp in experience:
            title    = html.escape((exp.get("title") or "").strip())
            company  = html.escape((exp.get("company") or "").strip())
            duration = html.escape((exp.get("duration") or "").strip())
            bullets  = [b.strip() for b in (exp.get("bullets") or []) if b and b.strip()]

            left_text = f"<b>{title}</b>"
            if company:
                left_text += f" \u2014 {company}"

            # Header row (title + date) — KEEP together with first bullet
            header_block = [
                _title_date_row(left_text, duration, styles, W)
            ]
            if bullets:
                header_block.append(_bullet_row(bullets[0], styles, W))

            story.append(KeepTogether(header_block))

            # Remaining bullets — allowed to flow to next page if needed
            for b in bullets[1:]:
                story.append(_bullet_row(b, styles, W))

            story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════
    # PROJECTS
    # ═══════════════════════════════════════════════════════
    projects = resume_data.get("projects") or []
    if projects:
        story += _section_header("Projects", styles, W)

        for proj in projects:
            pname   = html.escape((proj.get("name") or "").strip())
            tech    = html.escape((proj.get("tech") or "").strip())
            bullets = [b.strip() for b in (proj.get("bullets") or []) if b and b.strip()]

            header_text = f"<b>{pname}</b>"
            if tech:
                header_text += f'  <font size="8.5" color="#4B5563"><i>{tech}</i></font>'

            header_block = [Paragraph(header_text, styles["role_title"])]
            if bullets:
                header_block.append(_bullet_row(bullets[0], styles, W))

            story.append(KeepTogether(header_block))

            for b in bullets[1:]:
                story.append(_bullet_row(b, styles, W))

            story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════
    # EDUCATION
    # ═══════════════════════════════════════════════════════
    education = resume_data.get("education") or []
    if education:
        story += _section_header("Education", styles, W)

        for edu in education:
            degree = html.escape((edu.get("degree") or "").strip())
            inst   = html.escape((edu.get("institution") or "").strip())
            year   = html.escape((edu.get("year") or "").strip())
            grade  = html.escape((edu.get("grade") or "").strip())

            block = [
                Table(
                    [[
                        Paragraph(f"<b>{degree}</b>", styles["edu_degree"]),
                        Paragraph(year, styles["meta"]),
                    ]],
                    colWidths=[W * 0.70, W * 0.30],
                    style=TableStyle([
                        ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
                        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                        ("TOPPADDING",    (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ])
                )
            ]
            if inst:
                block.append(Paragraph(inst, styles["edu_detail"]))
            if grade:
                block.append(Paragraph(
                    f'<font color="#4B5563">Grade: </font>{grade}',
                    styles["edu_detail"]
                ))
            block.append(Spacer(1, 3))
            story.append(KeepTogether(block))

    # ═══════════════════════════════════════════════════════
    # CERTIFICATIONS
    # ═══════════════════════════════════════════════════════
    certs = [c.strip() for c in (resume_data.get("certifications") or []) if c and c.strip()]
    if certs:
        story += _section_header("Certifications", styles, W)
        for cert in certs:
            story.append(_bullet_row(cert, styles, W, justify=False))
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════
    # ACHIEVEMENTS (optional — supported if AI returns them)
    # ═══════════════════════════════════════════════════════
    achievements = [a.strip() for a in (resume_data.get("achievements") or []) if a and a.strip()]
    if achievements:
        story += _section_header("Achievements", styles, W)
        for a in achievements:
            story.append(_bullet_row(a, styles, W, justify=False))
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════
    # LANGUAGES (optional)
    # ═══════════════════════════════════════════════════════
    languages = [l.strip() for l in (resume_data.get("languages") or []) if l and l.strip()]
    if languages:
        story += _section_header("Languages", styles, W)
        story.append(Paragraph(
            "  \u2022  ".join([html.escape(l) for l in languages]),
            styles["body"]
        ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()