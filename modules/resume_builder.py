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

# ── Colors ────────────────────────────────────────────────────
BLACK      = colors.HexColor("#111111")
DARK_GRAY  = colors.HexColor("#222222")
MID_GRAY   = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#888888")
LINE_COLOR = colors.HexColor("#bbbbbb")


def get_styles():
    return {
        "name": ParagraphStyle(
            "name", fontName="Helvetica-Bold", fontSize=20,
            textColor=BLACK, leading=24, spaceAfter=1, alignment=TA_LEFT
        ),
        "target_role": ParagraphStyle(
            "target_role", fontName="Helvetica", fontSize=10,
            textColor=MID_GRAY, leading=14, spaceAfter=2, alignment=TA_LEFT
        ),
        "contact": ParagraphStyle(
            "contact", fontName="Helvetica", fontSize=8.5,
            textColor=MID_GRAY, leading=12, spaceAfter=3, alignment=TA_LEFT
        ),
        "section_title": ParagraphStyle(
            "section_title", fontName="Helvetica-Bold", fontSize=9,
            textColor=BLACK, leading=13, spaceBefore=8, spaceAfter=2
        ),
        "job_title_left": ParagraphStyle(
            "job_title_left", fontName="Helvetica-Bold", fontSize=10,
            textColor=BLACK, leading=14, spaceBefore=5, spaceAfter=0
        ),
        "job_meta_right": ParagraphStyle(
            "job_meta_right", fontName="Helvetica-Oblique", fontSize=9,
            textColor=LIGHT_GRAY, leading=14, alignment=TA_LEFT
        ),
        "company": ParagraphStyle(
            "company", fontName="Helvetica-Oblique", fontSize=9,
            textColor=MID_GRAY, leading=12, spaceAfter=2
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=9.5,
            textColor=DARK_GRAY, leading=14,
            leftIndent=12, firstLineIndent=-8,
            spaceAfter=2, alignment=TA_JUSTIFY
        ),
        "summary": ParagraphStyle(
            "summary", fontName="Helvetica", fontSize=9.5,
            textColor=DARK_GRAY, leading=15,
            spaceAfter=4, alignment=TA_JUSTIFY
        ),
        "skills_text": ParagraphStyle(
            "skills_text", fontName="Helvetica", fontSize=9.5,
            textColor=DARK_GRAY, leading=15,
            spaceAfter=2, alignment=TA_LEFT
        ),
        "edu_title": ParagraphStyle(
            "edu_title", fontName="Helvetica-Bold", fontSize=10,
            textColor=BLACK, leading=14, spaceBefore=4
        ),
        "edu_detail": ParagraphStyle(
            "edu_detail", fontName="Helvetica", fontSize=9,
            textColor=MID_GRAY, leading=13
        ),
    }


def section_header(title, styles, W):
    """Uppercase section title with a thin horizontal rule below."""
    return [
        Spacer(1, 5),
        Paragraph(title.upper(), styles["section_title"]),
        HRFlowable(
            width="100%", thickness=0.5, color=LINE_COLOR,
            spaceBefore=1, spaceAfter=5
        ),
    ]


def build_resume_pdf(resume_data: dict) -> bytes:
    buffer = io.BytesIO()
    styles = get_styles()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )
    W = A4[0] - 30*mm   # usable content width
    story = []

    # ── HEADER ────────────────────────────────────────────────
    name     = resume_data.get("name", "")
    role     = resume_data.get("target_role", "")
    email    = resume_data.get("email", "")
    phone    = resume_data.get("phone", "")
    linkedin = resume_data.get("linkedin", "")
    github   = resume_data.get("github", "")
    location = resume_data.get("location", "")

    if name:
        story.append(Paragraph(name, styles["name"]))
    if role:
        story.append(Paragraph(role, styles["target_role"]))

    contact_parts = [x for x in [email, phone, location, linkedin, github] if x]
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), styles["contact"]))

    story.append(HRFlowable(
        width="100%", thickness=1.2, color=BLACK,
        spaceBefore=4, spaceAfter=0
    ))

    # ── SUMMARY ───────────────────────────────────────────────
    summary = resume_data.get("summary", "")
    if summary:
        story += section_header("Summary", styles, W)
        story.append(Paragraph(summary, styles["summary"]))

    # ── SKILLS ────────────────────────────────────────────────
    # Displayed as a 4-column grid, each cell is one skill with a bullet
    skills = resume_data.get("skills", [])
    if skills:
        story += section_header("Skills", styles, W)
        row_size = 4
        col_w    = W / row_size
        rows     = [skills[i:i+row_size] for i in range(0, len(skills), row_size)]
        table_data = []
        for row in rows:
            while len(row) < row_size:
                row.append("")
            table_data.append([
                Paragraph(f"• {s}" if s else "", styles["skills_text"])
                for s in row
            ])
        t = Table(table_data, colWidths=[col_w] * row_size)
        t.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 2),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 2),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        story.append(t)

    # ── EXPERIENCE ────────────────────────────────────────────
    experience = resume_data.get("experience", [])
    if experience:
        story += section_header("Experience", styles, W)
        for exp in experience:
            title_str    = exp.get("title", "")
            company_str  = exp.get("company", "")
            duration_str = exp.get("duration", "")

            # Job title on left, date on right — same row
            header_row = Table(
                [[
                    Paragraph(title_str, styles["job_title_left"]),
                    Paragraph(duration_str, styles["job_meta_right"]),
                ]],
                colWidths=[W * 0.68, W * 0.32]
            )
            header_row.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("ALIGN",         (1, 0), (1,  0),  "RIGHT"),
            ]))
            story.append(header_row)

            if company_str:
                story.append(Paragraph(company_str, styles["company"]))

            for b in exp.get("bullets", []):
                story.append(Paragraph(f"\u2022  {b}", styles["bullet"]))
            story.append(Spacer(1, 4))

    # ── PROJECTS ──────────────────────────────────────────────
    projects = resume_data.get("projects", [])
    if projects:
        story += section_header("Projects", styles, W)
        for proj in projects:
            proj_name = proj.get("name", "")
            tech      = proj.get("tech", "")
            header    = f"<b>{proj_name}</b>"
            if tech:
                header += f"  <font size='8' color='#777777'>| {tech}</font>"
            story.append(Paragraph(header, styles["job_title_left"]))
            for b in proj.get("bullets", []):
                story.append(Paragraph(f"\u2022  {b}", styles["bullet"]))
            story.append(Spacer(1, 4))

    # ── EDUCATION ─────────────────────────────────────────────
    education = resume_data.get("education", [])
    if education:
        story += section_header("Education", styles, W)
        for edu in education:
            degree = edu.get("degree", "")
            inst   = edu.get("institution", "")
            year   = edu.get("year", "")
            grade  = edu.get("grade", "")

            edu_row = Table(
                [[
                    Paragraph(f"<b>{degree}</b>  —  {inst}", styles["edu_title"]),
                    Paragraph(year, styles["job_meta_right"]),
                ]],
                colWidths=[W * 0.75, W * 0.25]
            )
            edu_row.setStyle(TableStyle([
                ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING",   (0, 0), (-1, -1), 0),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("ALIGN",         (1, 0), (1,  0),  "RIGHT"),
            ]))
            story.append(edu_row)
            if grade:
                story.append(Paragraph(grade, styles["edu_detail"]))
            story.append(Spacer(1, 3))

    # ── CERTIFICATIONS ────────────────────────────────────────
    certs = resume_data.get("certifications", [])
    if certs:
        story += section_header("Certifications", styles, W)
        for cert in certs:
            story.append(Paragraph(f"\u2022  {cert}", styles["bullet"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()