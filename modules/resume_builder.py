from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import io

# ── Colors (all neutral, professional) ───────────────────────
BLACK      = colors.HexColor("#111111")
DARK_GRAY  = colors.HexColor("#222222")
MID_GRAY   = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#777777")
LINE_COLOR = colors.HexColor("#cccccc")
ACCENT     = colors.HexColor("#1a1a1a")  # near black, no blue


def get_styles():
    return {
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=BLACK,
            leading=24,
            spaceAfter=2,
            alignment=TA_LEFT,
        ),
        "target_role": ParagraphStyle(
            "target_role",
            fontName="Helvetica",
            fontSize=10,
            textColor=MID_GRAY,
            leading=14,
            spaceAfter=3,
            alignment=TA_LEFT,
        ),
        "contact": ParagraphStyle(
            "contact",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=MID_GRAY,
            leading=12,
            spaceAfter=4,
            alignment=TA_LEFT,
        ),
        "section_title": ParagraphStyle(
            "section_title",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=BLACK,
            leading=13,
            spaceBefore=8,
            spaceAfter=2,
        ),
        "job_title": ParagraphStyle(
            "job_title",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=BLACK,
            leading=14,
            spaceBefore=5,
            spaceAfter=1,
        ),
        "job_meta": ParagraphStyle(
            "job_meta",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            textColor=LIGHT_GRAY,
            leading=12,
            alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK_GRAY,
            leading=14,
            leftIndent=10,
            spaceAfter=2,
            alignment=TA_JUSTIFY,
        ),
        "summary": ParagraphStyle(
            "summary",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK_GRAY,
            leading=15,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
        ),
        "skill": ParagraphStyle(
            "skill",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK_GRAY,
            leading=14,
            alignment=TA_LEFT,
        ),
        "edu_title": ParagraphStyle(
            "edu_title",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=BLACK,
            leading=14,
            spaceBefore=5,
        ),
        "edu_detail": ParagraphStyle(
            "edu_detail",
            fontName="Helvetica",
            fontSize=9,
            textColor=MID_GRAY,
            leading=13,
        ),
    }


def section_header(title, styles):
    """Clean uppercase section header with a thin line."""
    return [
        Spacer(1, 6),
        Paragraph(title.upper(), styles["section_title"]),
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=LINE_COLOR,
            spaceBefore=2,
            spaceAfter=4,
        ),
    ]


def build_resume_pdf(resume_data: dict) -> bytes:
    buffer = io.BytesIO()
    styles = get_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=16*mm,
        bottomMargin=16*mm,
    )

    W = A4[0] - 40*mm  # usable width
    story = []

    # ── HEADER ────────────────────────────────────────────────
    name = resume_data.get("name", "")
    role = resume_data.get("target_role", "")
    email = resume_data.get("email", "")
    phone = resume_data.get("phone", "")
    linkedin = resume_data.get("linkedin", "")
    github = resume_data.get("github", "")
    location = resume_data.get("location", "")

    if name:
        story.append(Paragraph(name, styles["name"]))
    if role:
        story.append(Paragraph(role, styles["target_role"]))

    contact_parts = [x for x in [email, phone, location, linkedin, github] if x]
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), styles["contact"]))

    story.append(HRFlowable(
        width="100%", thickness=1,
        color=BLACK, spaceBefore=3, spaceAfter=0
    ))

    # ── SUMMARY ───────────────────────────────────────────────
    summary = resume_data.get("summary", "")
    if summary:
        story += section_header("Summary", styles)
        story.append(Paragraph(summary, styles["summary"]))

    # ── SKILLS ────────────────────────────────────────────────
    skills = resume_data.get("skills", [])
    if skills:
        story += section_header("Skills", styles)
        # Skills as comma-separated single line (cleaner, ATS-friendly)
        skills_text = "  •  ".join(skills)
        story.append(Paragraph(skills_text, styles["skill"]))

    # ── EXPERIENCE ────────────────────────────────────────────
    experience = resume_data.get("experience", [])
    if experience:
        story += section_header("Experience", styles)
        for exp in experience:
            title_str = exp.get("title", "")
            company_str = exp.get("company", "")
            duration_str = exp.get("duration", "")

            # Title on left, duration on right
            row = Table(
                [[
                    Paragraph(f"{title_str}  —  {company_str}", styles["job_title"]),
                    Paragraph(duration_str, styles["job_meta"]),
                ]],
                colWidths=[W * 0.72, W * 0.28]
            )
            row.setStyle(TableStyle([
                ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
                ("LEFTPADDING",   (0,0), (-1,-1), 0),
                ("RIGHTPADDING",  (0,0), (-1,-1), 0),
                ("TOPPADDING",    (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
                ("ALIGN",         (1,0), (1,0),   "RIGHT"),
            ]))
            story.append(row)

            for b in exp.get("bullets", []):
                story.append(Paragraph(f"• {b}", styles["bullet"]))
            story.append(Spacer(1, 4))

    # ── PROJECTS ──────────────────────────────────────────────
    projects = resume_data.get("projects", [])
    if projects:
        story += section_header("Projects", styles)
        for proj in projects:
            proj_name = proj.get("name", "")
            tech = proj.get("tech", "")
            header = f"<b>{proj_name}</b>"
            if tech:
                header += f"  |  <font size='8' color='#666666'>{tech}</font>"
            story.append(Paragraph(header, styles["job_title"]))
            for b in proj.get("bullets", []):
                story.append(Paragraph(f"• {b}", styles["bullet"]))
            story.append(Spacer(1, 4))

    # ── EDUCATION ─────────────────────────────────────────────
    education = resume_data.get("education", [])
    if education:
        story += section_header("Education", styles)
        for edu in education:
            degree = edu.get("degree", "")
            inst = edu.get("institution", "")
            year = edu.get("year", "")
            grade = edu.get("grade", "")

            row = Table(
                [[
                    Paragraph(f"{degree}  —  {inst}", styles["edu_title"]),
                    Paragraph(year, styles["job_meta"]),
                ]],
                colWidths=[W * 0.75, W * 0.25]
            )
            row.setStyle(TableStyle([
                ("VALIGN",        (0,0), (-1,-1), "BOTTOM"),
                ("LEFTPADDING",   (0,0), (-1,-1), 0),
                ("RIGHTPADDING",  (0,0), (-1,-1), 0),
                ("TOPPADDING",    (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
                ("ALIGN",         (1,0), (1,0),   "RIGHT"),
            ]))
            story.append(row)
            if grade:
                story.append(Paragraph(grade, styles["edu_detail"]))
            story.append(Spacer(1, 4))

    # ── CERTIFICATIONS ────────────────────────────────────────
    certs = resume_data.get("certifications", [])
    if certs:
        story += section_header("Certifications", styles)
        for cert in certs:
            story.append(Paragraph(f"• {cert}", styles["bullet"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()