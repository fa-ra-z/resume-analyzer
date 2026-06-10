from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_JUSTIFY
import io

# ─────────────────────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────────────────────
C_NAME        = colors.HexColor("#0D0D0D")
C_HEADING     = colors.HexColor("#1A1A2E")
C_ACCENT      = colors.HexColor("#2563EB")
C_BODY        = colors.HexColor("#1F1F1F")
C_MUTED       = colors.HexColor("#4B5563")
C_RULE        = colors.HexColor("#D1D5DB")


# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
def get_styles():
    BASE = 9.5
    LH   = 14

    return {
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=C_NAME,
            leading=26,
            spaceAfter=1,
            alignment=TA_LEFT,
        ),
        "tagline": ParagraphStyle(
            "tagline",
            fontName="Helvetica",
            fontSize=10.5,
            textColor=C_MUTED,
            leading=14,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        "contact": ParagraphStyle(
            "contact",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=C_MUTED,
            leading=12,
            spaceAfter=5,
            alignment=TA_LEFT,
        ),
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            textColor=C_HEADING,
            leading=12,
            spaceBefore=10,
            spaceAfter=2,
        ),
        "role_title": ParagraphStyle(
            "role_title",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_BODY,
            leading=14,
            spaceBefore=6,
            spaceAfter=0,
        ),
        "meta": ParagraphStyle(
            "meta",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            textColor=C_MUTED,
            leading=13,
            spaceAfter=3,
        ),
        # ── BULLETS: use ReportLab's native bullet system ──
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=LH,
            leftIndent=14,         # body indent
            bulletIndent=2,        # bullet dot position
            spaceAfter=2.5,
            alignment=TA_JUSTIFY,
            bulletFontName="Helvetica-Bold",
            bulletFontSize=BASE,
        ),
        "summary": ParagraphStyle(
            "summary",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=15,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
        ),
        "skill": ParagraphStyle(
            "skill",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=LH,
            leftIndent=12,
            bulletIndent=2,
            alignment=TA_LEFT,
            spaceAfter=2,
            bulletFontName="Helvetica-Bold",
            bulletFontSize=BASE,
        ),
        "edu_degree": ParagraphStyle(
            "edu_degree",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_BODY,
            leading=14,
            spaceBefore=5,
            spaceAfter=0,
        ),
        "edu_detail": ParagraphStyle(
            "edu_detail",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=C_MUTED,
            leading=13,
            spaceAfter=2,
        ),
        "cert": ParagraphStyle(
            "cert",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=LH,
            leftIndent=14,
            bulletIndent=2,
            spaceAfter=2,
            bulletFontName="Helvetica-Bold",
            bulletFontSize=BASE,
        ),
    }


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _section_header(title: str, styles: dict, W: float) -> list:
    return [
        Spacer(1, 4),
        Paragraph(title.upper(), styles["section"]),
        HRFlowable(
            width=W,
            thickness=0.6,
            color=C_RULE,
            spaceBefore=1,
            spaceAfter=4,
        ),
    ]


def _bullet(text: str, styles: dict, style_key: str = "bullet") -> Paragraph:
    """
    Creates a properly-aligned bullet using ReportLab's native bullet system.
    This GUARANTEES that wrapped lines align under the first character of text,
    not under the bullet dot.
    """
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(
        safe,
        styles[style_key],
        bulletText="\u2022",   # • bullet character handled by ReportLab
    )


def _two_col_row(left_para, right_para, W: float) -> Table:
    t = Table(
        [[left_para, right_para]],
        colWidths=[W * 0.74, W * 0.26],
    )
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("ALIGN",         (1, 0), (1, 0),   "RIGHT"),
    ]))
    return t


# ─────────────────────────────────────────────────────────────
# MAIN PDF BUILDER
# ─────────────────────────────────────────────────────────────
def build_resume_pdf(resume_data: dict) -> bytes:
    buffer = io.BytesIO()
    styles = get_styles()

    LEFT   = 18 * mm
    RIGHT  = 18 * mm
    TOP    = 16 * mm
    BOTTOM = 14 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
        title=resume_data.get("name", "Resume"),
        author=resume_data.get("name", ""),
        subject=resume_data.get("target_role", "Resume"),
        creator="ResumeIQ",
    )

    W = A4[0] - LEFT - RIGHT
    story = []

    # ══════════════════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════════════════
    name     = resume_data.get("name", "").strip()
    tagline  = resume_data.get("target_role", "").strip()
    email    = resume_data.get("email", "").strip()
    phone    = resume_data.get("phone", "").strip()
    linkedin = resume_data.get("linkedin", "").strip()
    github   = resume_data.get("github", "").strip()
    location = resume_data.get("location", "").strip()

    if name:
        story.append(Paragraph(name, styles["name"]))

    story.append(
        HRFlowable(
            width=W,
            thickness=2,
            color=C_ACCENT,
            spaceBefore=0,
            spaceAfter=3,
        )
    )

    if tagline:
        story.append(Paragraph(tagline, styles["tagline"]))

    contact_parts = []
    if email:    contact_parts.append(email)
    if phone:    contact_parts.append(phone)
    if location: contact_parts.append(location)
    if linkedin:
        label = "LinkedIn: " + (
            linkedin.split("linkedin.com/in/")[-1].rstrip("/")
            if "linkedin.com" in linkedin else linkedin
        )
        contact_parts.append(label)
    if github:
        label = "GitHub: " + (
            github.split("github.com/")[-1].rstrip("/")
            if "github.com" in github else github
        )
        contact_parts.append(label)

    if contact_parts:
        separator = "  \u2022  "
        story.append(
            Paragraph(separator.join(contact_parts), styles["contact"])
        )

    story.append(
        HRFlowable(
            width=W,
            thickness=0.5,
            color=C_RULE,
            spaceBefore=2,
            spaceAfter=0,
        )
    )

    # ══════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════
    summary = resume_data.get("summary", "").strip()
    if summary:
        story += _section_header("Professional Summary", styles, W)
        story.append(Paragraph(summary, styles["summary"]))

    # ══════════════════════════════════════════════════════
    # SKILLS — clean 3-column grid using inner tables
    # ══════════════════════════════════════════════════════
    skills = [s.strip() for s in resume_data.get("skills", []) if s.strip()]
    if skills:
        story += _section_header("Technical Skills", styles, W)

        COLS = 3
        while len(skills) % COLS != 0:
            skills.append("")

        # Distribute skills column-by-column (vertical fill, like newspaper columns)
        rows_count = len(skills) // COLS
        grid = [["" for _ in range(COLS)] for _ in range(rows_count)]
        for idx, skill in enumerate(skills):
            col = idx // rows_count
            row = idx % rows_count
            if col < COLS:
                grid[row][col] = skill

        table_data = []
        for row in grid:
            cells = []
            for s in row:
                if s:
                    # Each skill cell is a mini-table: [dot] [text]
                    inner = Table(
                        [[
                            Paragraph(
                                f'<font color="#2563EB"><b>\u2022</b></font>',
                                ParagraphStyle("dot",
                                    fontName="Helvetica-Bold",
                                    fontSize=9.5,
                                    textColor=C_ACCENT,
                                    leading=14,
                                )
                            ),
                            Paragraph(
                                s,
                                ParagraphStyle("st",
                                    fontName="Helvetica",
                                    fontSize=9.5,
                                    textColor=C_BODY,
                                    leading=14,
                                )
                            )
                        ]],
                        colWidths=[8, None],
                    )
                    inner.setStyle(TableStyle([
                        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                        ("TOPPADDING",    (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]))
                    cells.append(inner)
                else:
                    cells.append("")
            table_data.append(cells)

        col_w = W / COLS
        skill_table = Table(table_data, colWidths=[col_w] * COLS)
        skill_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(skill_table)

    # ══════════════════════════════════════════════════════
    # EXPERIENCE
    # ══════════════════════════════════════════════════════
    experience = resume_data.get("experience", [])
    if experience:
        story += _section_header("Professional Experience", styles, W)

        for exp in experience:
            title    = exp.get("title", "").strip()
            company  = exp.get("company", "").strip()
            duration = exp.get("duration", "").strip()
            bullets  = [b.strip() for b in exp.get("bullets", []) if b.strip()]

            left_text  = f"<b>{title}</b>" + (f"  —  {company}" if company else "")
            right_text = duration

            block = [
                _two_col_row(
                    Paragraph(left_text,  styles["role_title"]),
                    Paragraph(right_text, styles["meta"]),
                    W,
                )
            ]
            for b in bullets:
                block.append(_bullet(b, styles))
            block.append(Spacer(1, 3))

            story.append(KeepTogether(block))

    # ══════════════════════════════════════════════════════
    # PROJECTS
    # ══════════════════════════════════════════════════════
    projects = resume_data.get("projects", [])
    if projects:
        story += _section_header("Projects", styles, W)

        for proj in projects:
            pname   = proj.get("name", "").strip()
            tech    = proj.get("tech", "").strip()
            bullets = [b.strip() for b in proj.get("bullets", []) if b.strip()]

            header_text = f"<b>{pname}</b>"
            if tech:
                safe_tech = tech.replace("&", "&amp;")
                header_text += (
                    f'  <font size="8.5" color="#4B5563"><i>{safe_tech}</i></font>'
                )

            block = [Paragraph(header_text, styles["role_title"])]
            for b in bullets:
                block.append(_bullet(b, styles))
            block.append(Spacer(1, 3))

            story.append(KeepTogether(block))

    # ══════════════════════════════════════════════════════
    # EDUCATION
    # ══════════════════════════════════════════════════════
    education = resume_data.get("education", [])
    if education:
        story += _section_header("Education", styles, W)

        for edu in education:
            degree = edu.get("degree", "").strip()
            inst   = edu.get("institution", "").strip()
            year   = edu.get("year", "").strip()
            grade  = edu.get("grade", "").strip()

            block = [
                _two_col_row(
                    Paragraph(f"<b>{degree}</b>", styles["edu_degree"]),
                    Paragraph(year, styles["meta"]),
                    W,
                )
            ]
            if inst:
                block.append(Paragraph(inst, styles["edu_detail"]))
            if grade:
                block.append(
                    Paragraph(
                        f'<font color="#4B5563">Grade: </font>{grade}',
                        styles["edu_detail"]
                    )
                )
            block.append(Spacer(1, 3))

            story.append(KeepTogether(block))

    # ══════════════════════════════════════════════════════
    # CERTIFICATIONS
    # ══════════════════════════════════════════════════════
    certs = [c.strip() for c in resume_data.get("certifications", []) if c.strip()]
    if certs:
        story += _section_header("Certifications", styles, W)
        for cert in certs:
            story.append(_bullet(cert, styles, style_key="cert"))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()