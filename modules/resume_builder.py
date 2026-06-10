from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# ─────────────────────────────────────────────────────────────
# COLOR PALETTE  — clean, professional, ATS-safe
# ─────────────────────────────────────────────────────────────
C_NAME        = colors.HexColor("#0D0D0D")   # near-black for name
C_HEADING     = colors.HexColor("#1A1A2E")   # deep navy for section titles
C_ACCENT      = colors.HexColor("#2563EB")   # blue accent line under name
C_BODY        = colors.HexColor("#1F1F1F")   # body text
C_MUTED       = colors.HexColor("#4B5563")   # company / date / meta
C_RULE        = colors.HexColor("#D1D5DB")   # section divider lines
C_BULLET_DOT  = colors.HexColor("#2563EB")   # bullet dot colour


# ─────────────────────────────────────────────────────────────
# TYPOGRAPHY  — all built-in Helvetica (universally embedded)
# ─────────────────────────────────────────────────────────────
def get_styles():
    BASE = 9.5   # body font size in points
    LH   = 14    # standard line height

    return {

        # ── Name ──────────────────────────────────────────
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=C_NAME,
            leading=26,
            spaceAfter=1,
            alignment=TA_LEFT,
            letterSpacing=0.5,
        ),

        # ── Target role tag line ───────────────────────────
        "tagline": ParagraphStyle(
            "tagline",
            fontName="Helvetica",
            fontSize=10.5,
            textColor=C_MUTED,
            leading=14,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),

        # ── Contact bar ───────────────────────────────────
        "contact": ParagraphStyle(
            "contact",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=C_MUTED,
            leading=12,
            spaceAfter=5,
            alignment=TA_LEFT,
        ),

        # ── Section heading (EXPERIENCE, SKILLS …) ────────
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            textColor=C_HEADING,
            leading=12,
            spaceBefore=10,
            spaceAfter=2,
            letterSpacing=1.4,       # wide-tracked caps feel premium
        ),

        # ── Job / project title (bold, black) ─────────────
        "role_title": ParagraphStyle(
            "role_title",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_BODY,
            leading=14,
            spaceBefore=6,
            spaceAfter=0,
        ),

        # ── Company + date meta line ───────────────────────
        "meta": ParagraphStyle(
            "meta",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            textColor=C_MUTED,
            leading=13,
            spaceAfter=3,
        ),

        # ── Bullet point ──────────────────────────────────
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=LH,
            leftIndent=12,
            firstLineIndent=-12,
            spaceAfter=2.5,
            alignment=TA_JUSTIFY,
        ),

        # ── Professional summary paragraph ────────────────
        "summary": ParagraphStyle(
            "summary",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=15,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
        ),

        # ── Skill pill text ───────────────────────────────
        "skill": ParagraphStyle(
            "skill",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=LH,
            leftIndent=10,
            firstLineIndent=-10,
            alignment=TA_LEFT,
            spaceAfter=2,
        ),

        # ── Education degree line ─────────────────────────
        "edu_degree": ParagraphStyle(
            "edu_degree",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_BODY,
            leading=14,
            spaceBefore=5,
            spaceAfter=0,
        ),

        # ── Education detail (institution / grade) ────────
        "edu_detail": ParagraphStyle(
            "edu_detail",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=C_MUTED,
            leading=13,
            spaceAfter=2,
        ),

        # ── Certification entry ───────────────────────────
        "cert": ParagraphStyle(
            "cert",
            fontName="Helvetica",
            fontSize=BASE,
            textColor=C_BODY,
            leading=LH,
            leftIndent=12,
            firstLineIndent=-12,
            spaceAfter=2,
        ),
    }


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _section_header(title: str, styles: dict, W: float) -> list:
    """Returns [spacer, ALL-CAPS heading, thin accent rule] as a KeepTogether block."""
    items = [
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
    return [KeepTogether(items)]


def _bullet_line(text: str, styles: dict) -> Paragraph:
    """Single bullet with a unicode bullet dot, properly indented."""
    # Use HTML-safe bullet character
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(
        f'<font color="#2563EB">\u2022</font>  {safe}',
        styles["bullet"]
    )


def _two_col_row(left_para, right_para, W: float) -> Table:
    """Utility: two-column table row (title left, date right)."""
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
    """
    Builds a pixel-perfect, ATS-safe, HR-ready single-page PDF resume.

    Parameters
    ----------
    resume_data : dict
        Structured resume data returned by the AI optimizer.

    Returns
    -------
    bytes
        Raw PDF bytes ready for st.download_button.
    """
    buffer = io.BytesIO()
    styles = get_styles()

    # ── Page geometry ─────────────────────────────────────
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

    # Usable width after margins
    W = A4[0] - LEFT - RIGHT
    story = []

    # ══════════════════════════════════════════════════════
    # 1. HEADER — Name · Role · Contact
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

    # Blue accent rule immediately under name
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

    # Build contact line — only include non-empty fields
    contact_parts = []
    if email:
        contact_parts.append(email)
    if phone:
        contact_parts.append(phone)
    if location:
        contact_parts.append(location)
    if linkedin:
        # Show clean label instead of full URL if URL is long
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
        separator = "  \u2022  "          # spaced bullet separator
        story.append(
            Paragraph(separator.join(contact_parts), styles["contact"])
        )

    # Thin full-width rule to close the header block
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
    # 2. PROFESSIONAL SUMMARY
    # ══════════════════════════════════════════════════════
    summary = resume_data.get("summary", "").strip()
    if summary:
        story += _section_header("Professional Summary", styles, W)
        story.append(Paragraph(summary, styles["summary"]))

    # ══════════════════════════════════════════════════════
    # 3. SKILLS  — 3-column grid
    # ══════════════════════════════════════════════════════
    skills = [s.strip() for s in resume_data.get("skills", []) if s.strip()]
    if skills:
        story += _section_header("Technical Skills", styles, W)

        COLS = 3
        # Pad to fill last row
        while len(skills) % COLS != 0:
            skills.append("")

        rows = [skills[i:i + COLS] for i in range(0, len(skills), COLS)]
        table_data = []
        for row in rows:
            table_data.append([
                Paragraph(
                    f'<font color="#2563EB">\u2022</font>  {s}' if s else "",
                    styles["skill"]
                )
                for s in row
            ])

        col_w = W / COLS
        skill_table = Table(table_data, colWidths=[col_w] * COLS)
        skill_table.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 2),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
            ("TOPPADDING",    (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        story.append(skill_table)

    # ══════════════════════════════════════════════════════
    # 4. EXPERIENCE
    # ══════════════════════════════════════════════════════
    experience = resume_data.get("experience", [])
    if experience:
        story += _section_header("Professional Experience", styles, W)

        for exp in experience:
            title    = exp.get("title", "").strip()
            company  = exp.get("company", "").strip()
            duration = exp.get("duration", "").strip()
            bullets  = [b.strip() for b in exp.get("bullets", []) if b.strip()]

            # Title + company on one line, duration right-aligned
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
                block.append(_bullet_line(b, styles))
            block.append(Spacer(1, 3))

            story.append(KeepTogether(block))

    # ══════════════════════════════════════════════════════
    # 5. PROJECTS
    # ══════════════════════════════════════════════════════
    projects = resume_data.get("projects", [])
    if projects:
        story += _section_header("Projects", styles, W)

        for proj in projects:
            pname   = proj.get("name", "").strip()
            tech    = proj.get("tech", "").strip()
            bullets = [b.strip() for b in proj.get("bullets", []) if b.strip()]

            # Project name bold, tech stack muted italic
            header_text = f"<b>{pname}</b>"
            if tech:
                safe_tech = tech.replace("&", "&amp;")
                header_text += (
                    f'  <font size="8.5" color="#4B5563"><i>{safe_tech}</i></font>'
                )

            block = [Paragraph(header_text, styles["role_title"])]
            for b in bullets:
                block.append(_bullet_line(b, styles))
            block.append(Spacer(1, 3))

            story.append(KeepTogether(block))

    # ══════════════════════════════════════════════════════
    # 6. EDUCATION
    # ══════════════════════════════════════════════════════
    education = resume_data.get("education", [])
    if education:
        story += _section_header("Education", styles, W)

        for edu in education:
            degree  = edu.get("degree", "").strip()
            inst    = edu.get("institution", "").strip()
            year    = edu.get("year", "").strip()
            grade   = edu.get("grade", "").strip()

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
    # 7. CERTIFICATIONS
    # ══════════════════════════════════════════════════════
    certs = [c.strip() for c in resume_data.get("certifications", []) if c.strip()]
    if certs:
        story += _section_header("Certifications", styles, W)
        for cert in certs:
            story.append(
                Paragraph(
                    f'<font color="#2563EB">\u2022</font>  {cert}',
                    styles["cert"]
                )
            )
        story.append(Spacer(1, 4))

    # ── Build the PDF ─────────────────────────────────────
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()