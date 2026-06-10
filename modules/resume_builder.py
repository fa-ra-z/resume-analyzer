from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
import io


# ── Color Palette ─────────────────────────────────────────────
BLACK      = colors.HexColor("#0f0f0f")
DARK_GRAY  = colors.HexColor("#2d2d2d")
MID_GRAY   = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#888888")
ACCENT     = colors.HexColor("#2563eb")   # professional blue
WHITE      = colors.white
LINE_COLOR = colors.HexColor("#d1d5db")


# ── Styles ────────────────────────────────────────────────────
def get_styles():
    return {
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=BLACK,
            leading=26,
            spaceAfter=2,
        ),
        "contact": ParagraphStyle(
            "contact",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=MID_GRAY,
            leading=12,
            alignment=TA_CENTER,
        ),
        "section_title": ParagraphStyle(
            "section_title",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=ACCENT,
            leading=14,
            spaceBefore=10,
            spaceAfter=3,
            textTransform="uppercase",
            letterSpacing=1.2,
        ),
        "job_title": ParagraphStyle(
            "job_title",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=BLACK,
            leading=14,
            spaceBefore=6,
        ),
        "job_meta": ParagraphStyle(
            "job_meta",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=LIGHT_GRAY,
            leading=12,
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK_GRAY,
            leading=14,
            leftIndent=12,
            bulletIndent=0,
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
        "skill_tag": ParagraphStyle(
            "skill_tag",
            fontName="Helvetica",
            fontSize=9,
            textColor=DARK_GRAY,
            leading=13,
        ),
        "edu_school": ParagraphStyle(
            "edu_school",
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
    """Returns a styled section header with a line underneath."""
    return [
        Spacer(1, 4),
        Paragraph(title, styles["section_title"]),
        HRFlowable(
            width="100%",
            thickness=0.6,
            color=LINE_COLOR,
            spaceAfter=5,
        ),
    ]


def build_resume_pdf(resume_data: dict) -> bytes:
    """
    Takes a structured resume dict and returns a PDF as bytes.

    resume_data keys:
        name, email, phone, linkedin, github, location,
        target_role, summary,
        skills (list of str),
        experience (list of {title, company, duration, bullets: [str]}),
        education (list of {degree, institution, year, grade}),
        projects (list of {name, tech, bullets: [str]}),
        certifications (list of str)
    """
    buffer = io.BytesIO()
    styles = get_styles()

    # Page margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=16*mm,
        bottomMargin=16*mm,
    )

    story = []
    W = A4[0] - 36*mm  # usable width

    # ── HEADER ────────────────────────────────────────────────
    name = resume_data.get("name", "Your Name")
    role = resume_data.get("target_role", "")
    email = resume_data.get("email", "")
    phone = resume_data.get("phone", "")
    linkedin = resume_data.get("linkedin", "")
    github = resume_data.get("github", "")
    location = resume_data.get("location", "")

    story.append(Paragraph(name, styles["name"]))

    if role:
        story.append(Paragraph(
            role,
            ParagraphStyle("role", fontName="Helvetica", fontSize=11,
                           textColor=ACCENT, leading=14, spaceAfter=4)
        ))

    contact_parts = [x for x in [email, phone, location, linkedin, github] if x]
    if contact_parts:
        story.append(Paragraph(
            "  ·  ".join(contact_parts),
            styles["contact"]
        ))

    story.append(HRFlowable(width="100%", thickness=1.5,
                            color=ACCENT, spaceBefore=6, spaceAfter=0))

    # ── SUMMARY ───────────────────────────────────────────────
    summary = resume_data.get("summary", "")
    if summary:
        story += section_header("Professional Summary", styles)
        story.append(Paragraph(summary, styles["summary"]))

    # ── SKILLS ────────────────────────────────────────────────
    skills = resume_data.get("skills", [])
    if skills:
        story += section_header("Technical Skills", styles)
        # Arrange skills in 3 columns
        cols = 3
        rows = [skills[i:i+cols] for i in range(0, len(skills), cols)]
        table_data = []
        for row in rows:
            while len(row) < cols:
                row.append("")
            table_data.append([
                Paragraph(f"• {s}", styles["skill_tag"]) for s in row
            ])
        col_w = W / cols
        t = Table(table_data, colWidths=[col_w]*cols)
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("TOPPADDING", (0,0), (-1,-1), 0),
        ]))
        story.append(t)

    # ── EXPERIENCE ────────────────────────────────────────────
    experience = resume_data.get("experience", [])
    if experience:
        story += section_header("Work Experience", styles)
        for exp in experience:
            # Title + Duration on same line
            title_duration = Table(
                [[
                    Paragraph(f"{exp.get('title','')} — {exp.get('company','')}", styles["job_title"]),
                    Paragraph(exp.get("duration", ""), styles["job_meta"]),
                ]],
                colWidths=[W*0.70, W*0.30]
            )
            title_duration.setStyle(TableStyle([
                ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
                ("LEFTPADDING", (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
                ("ALIGN", (1,0), (1,0), "RIGHT"),
            ]))
            story.append(title_duration)
            for bullet in exp.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", styles["bullet"]))
            story.append(Spacer(1, 4))

    # ── PROJECTS ──────────────────────────────────────────────
    projects = resume_data.get("projects", [])
    if projects:
        story += section_header("Projects", styles)
        for proj in projects:
            tech = proj.get("tech", "")
            proj_title = proj.get("name", "")
            header_text = f"<b>{proj_title}</b>"
            if tech:
                header_text += f"  <font color='#6b7280' size='8'>| {tech}</font>"
            story.append(Paragraph(header_text, styles["job_title"]))
            for bullet in proj.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", styles["bullet"]))
            story.append(Spacer(1, 4))

    # ── EDUCATION ─────────────────────────────────────────────
    education = resume_data.get("education", [])
    if education:
        story += section_header("Education", styles)
        for edu in education:
            edu_row = Table(
                [[
                    Paragraph(f"{edu.get('degree','')} — {edu.get('institution','')}", styles["edu_school"]),
                    Paragraph(edu.get("year", ""), styles["job_meta"]),
                ]],
                colWidths=[W*0.75, W*0.25]
            )
            edu_row.setStyle(TableStyle([
                ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
                ("LEFTPADDING", (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
                ("ALIGN", (1,0), (1,0), "RIGHT"),
            ]))
            story.append(edu_row)
            grade = edu.get("grade", "")
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