# academics/services/certificate_service.py
import os
from io import BytesIO

from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Avg

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas

from academics.models import (
    Certificate, StudentCourseProgress, Result, CourseUnit
)


# ==================================================================
# ELIGIBILITY
# ==================================================================

def is_course_unit_complete(student, course_unit):
    return StudentCourseProgress.objects.filter(
        student=student,
        course_unit=course_unit,
        is_completed=True,
        is_passed=True,
    ).exists()


def is_program_complete(student):
    progress_qs = StudentCourseProgress.objects.filter(student=student)
    if not progress_qs.exists():
        return False
    incomplete = progress_qs.filter(
        Q(is_completed=False) | Q(is_passed=False)
    ).exists()
    return not incomplete


def check_certificate_eligibility(student, certificate_type, course_unit=None):
    if certificate_type == 'course_completion':
        if not course_unit:
            return False, "A course unit is required for course completion certificates."
        if not is_course_unit_complete(student, course_unit):
            return False, f"Student has not completed {course_unit.code}."
        return True, "Eligible."

    if certificate_type == 'program_completion':
        if not is_program_complete(student):
            return False, "Student has not completed all required course units."
        return True, "Eligible."

    if certificate_type == 'transcript':
        if not Result.objects.filter(student=student).exists():
            return False, "No results available to generate a transcript."
        return True, "Eligible."

    if certificate_type == 'merit':
        results = Result.objects.filter(student=student, is_published=True)
        if not results.exists():
            return False, "No published results available."
        avg = results.aggregate(a=Avg('score'))['a'] or 0
        if avg < 75:
            return False, f"Average score {avg:.1f} is below the merit threshold (75)."
        return True, "Eligible."

    return False, "Unknown certificate type."


# ==================================================================
# SNAPSHOT
# ==================================================================

def build_snapshot(student, certificate_type, course_unit=None):
    progress = StudentCourseProgress.objects.filter(student=student)
    if course_unit:
        progress = progress.filter(course_unit=course_unit)

    results = Result.objects.filter(student=student, is_published=True)
    if course_unit:
        results = results.filter(course_unit=course_unit)

    course_name = None
    try:
        if hasattr(student, "course") and student.course:
            course_name = student.course.name
    except Exception:
        pass

    return {
        "student": {
            "registration_number": student.registration_number,
            "full_name": getattr(student, "full_name", str(student)),
            "course": course_name,
        },
        "certificate_type": certificate_type,
        "course_unit": {
            "code": course_unit.code,
            "name": course_unit.name,
        } if course_unit else None,
        "progress": [
            {
                "course_unit": p.course_unit.code,
                "score": float(p.score) if p.score is not None else None,
                "grade": p.grade,
            }
            for p in progress
        ],
        "results": [
            {
                "course_unit": r.course_unit.code,
                "score": float(r.score) if r.score is not None else None,
                "grade": r.grade,
            }
            for r in results
        ],
        "issued_at": timezone.now().isoformat(),
    }


# ==================================================================
# DEFAULT CONTENT
# ==================================================================

def get_default_content(certificate):
    """
    Build the certificate's default content from real data,
    falling back through snapshot -> live model -> empty string.
    """
    snap = certificate.snapshot_data or {}
    student_snap = snap.get("student", {})

    # ---- Student name ----
    student_name = (
        student_snap.get("full_name")
        or getattr(certificate.student, "full_name", None)
        or str(certificate.student)
    )

    # ---- Registration number ----
    reg_no = (
        student_snap.get("registration_number")
        or getattr(certificate.student, "registration_number", "")
        or ""
    )

    # ---- Programme / course name ----
    course_name = student_snap.get("course") or ""
    if not course_name:
        try:
            if hasattr(certificate.student, "course") and certificate.student.course:
                course_name = certificate.student.course.name
        except Exception:
            pass

    # ---- Dates ----
    issue_d = certificate.issue_date
    issue_long = issue_d.strftime("%d %B %Y") if issue_d else ""

    # ---- Issuer ----
    issuer_name = "Registrar"
    if certificate.issued_by:
        issuer_name = (
            certificate.issued_by.get_full_name()
            or getattr(certificate.issued_by, "username", "Registrar")
        )

    # ---- Course unit text ----
    cu = certificate.course_unit
    cu_text = f"{cu.code} — {cu.name}" if cu else (course_name or certificate.title)

    # ---------- PROGRAM COMPLETION ----------
    if certificate.certificate_type == 'program_completion':
        return {
            "intro_text": (
                "The Board of Governors and Academic Senate of the Institute "
                "hereby certify that"
            ),
            "student_name": student_name,
            "reg_no": reg_no,
            "body_text": (
                "having fulfilled all prescribed requirements of study, "
                "examinations, and continuous assessment, has been awarded the"
            ),
            "award_text": course_name or certificate.title,
            "closing_text": (
                f"with effect from the {issue_long}, and is hereby granted "
                "this Certificate with all rights, honours, and privileges "
                "appertaining thereto."
            ),
            "seal_text": (
                f"Given under the Official Seal of the Institute on this "
                f"{issue_long}."
            ),
            "signature_left_name": issuer_name,
            "signature_left_role": "Registrar",
            "signature_right_name": "Principal",
            "signature_right_role": "Director",
        }

    # ---------- COURSE COMPLETION ----------
    if certificate.certificate_type == 'course_completion':
        return {
            "intro_text": (
                "The Academic Senate of the Institute hereby certifies that"
            ),
            "student_name": student_name,
            "reg_no": reg_no,
            "body_text": "has successfully completed the course unit",
            "award_text": cu_text,
            "closing_text": (
                "having satisfied the requirements of continuous assessment "
                "and final examination."
            ),
            "seal_text": (
                f"Given under the Official Seal of the Institute on this "
                f"{issue_long}."
            ),
            "signature_left_name": issuer_name,
            "signature_left_role": "Registrar",
            "signature_right_name": "Principal",
            "signature_right_role": "Director",
        }

    # ---------- MERIT ----------
    if certificate.certificate_type == 'merit':
        return {
            "intro_text": (
                "The Academic Senate of the Institute takes great pleasure "
                "in certifying that"
            ),
            "student_name": student_name,
            "reg_no": reg_no,
            "body_text": (
                "has demonstrated outstanding academic excellence throughout "
                "the programme of study and is hereby awarded this"
            ),
            "award_text": "Certificate of Merit",
            "closing_text": "in recognition of distinguished scholarly achievement.",
            "seal_text": (
                f"Given under the Official Seal of the Institute on this "
                f"{issue_long}."
            ),
            "signature_left_name": issuer_name,
            "signature_left_role": "Registrar",
            "signature_right_name": "Principal",
            "signature_right_role": "Director",
        }

    # ---------- TRANSCRIPT ----------
    if certificate.certificate_type == 'transcript':
        return {
            "intro_text": "This is to certify that",
            "student_name": student_name,
            "reg_no": reg_no,
            "body_text": (
                "was a bona fide student of this Institute, and the grades "
                "recorded in the official academic record are hereby "
                "attested to be true and correct."
            ),
            "award_text": "",
            "closing_text": (
                "This transcript is issued upon request and remains the "
                "property of GLIDE Institute of Science and Technology."
            ),
            "seal_text": (
                f"Given under the Official Seal of the Institute on this "
                f"{issue_long}."
            ),
            "signature_left_name": issuer_name,
            "signature_left_role": "Registrar",
            "signature_right_name": "Principal",
            "signature_right_role": "Director",
        }

    # ---------- FALLBACK ----------
    return {
        "intro_text": "This is to certify that",
        "student_name": student_name,
        "reg_no": reg_no,
        "body_text": certificate.description or "",
        "award_text": certificate.title,
        "closing_text": "",
        "seal_text": (
            f"Given under the Official Seal of the Institute on this "
            f"{issue_long}."
        ),
        "signature_left_name": issuer_name,
        "signature_left_role": "Registrar",
        "signature_right_name": "Principal",
        "signature_right_role": "Director",
    }


def get_certificate_content(certificate):
    """
    Merge custom_content over defaults, so any missing key falls back
    to a real default. Result: certificate always looks filled in.
    """
    defaults = get_default_content(certificate)
    custom = certificate.custom_content or {}

    merged = dict(defaults)
    for key, value in custom.items():
        if value not in (None, ""):
            merged[key] = value
    return merged


# ==================================================================
# PDF HELPERS
# ==================================================================

def _find_logo_path():
    candidates = [
        os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
        os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png'),
        os.path.join(settings.BASE_DIR, 'static', 'logo.png'),
        os.path.join(settings.BASE_DIR, 'media', 'images', 'logo.png'),
        os.path.join(settings.BASE_DIR, 'media', 'logo.png'),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def _draw_ornaments(c, width, height):
    gold = colors.HexColor("#d4af37")
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    size = 32
    pad = 26
    c.line(pad, height - pad, pad + size, height - pad)
    c.line(pad, height - pad, pad, height - pad - size)
    c.line(width - pad, height - pad, width - pad - size, height - pad)
    c.line(width - pad, height - pad, width - pad, height - pad - size)
    c.line(pad, pad, pad + size, pad)
    c.line(pad, pad, pad, pad + size)
    c.line(width - pad, pad, width - pad - size, pad)
    c.line(width - pad, pad, width - pad, pad + size)


def _draw_seal(c, cx, cy, radius=42):
    gold = colors.HexColor("#b8860b")
    light_gold = colors.HexColor("#d4af37")
    navy = colors.HexColor("#223a66")

    c.setFillColor(light_gold)
    c.setStrokeColor(gold)
    c.setLineWidth(2)
    c.circle(cx, cy, radius, stroke=1, fill=1)

    c.setFillColor(colors.white)
    c.circle(cx, cy, radius - 6, stroke=0, fill=1)

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(cx, cy + 20, "GLIDE")

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(cx, cy - 2, "*")

    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(cx, cy - 18, "OFFICIAL")


# ==================================================================
# PDF GENERATION
# ==================================================================

def generate_certificate_pdf(certificate):
    buffer = BytesIO()
    width, height = landscape(A4)

    NAVY    = colors.HexColor("#223a66")
    CRIMSON = colors.HexColor("#e12454")
    GOLD    = colors.HexColor("#d4af37")
    CREAM   = colors.HexColor("#fdfaf3")

    c = pdf_canvas.Canvas(buffer, pagesize=landscape(A4))

    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, stroke=0, fill=1)

    c.setStrokeColor(NAVY)
    c.setLineWidth(6)
    c.rect(14, 14, width - 28, height - 28)

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.rect(24, 24, width - 48, height - 48)

    _draw_ornaments(c, width, height)

    # Header
    logo_path = _find_logo_path()
    left = 60
    top = height - 55

    if logo_path:
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, left, top - 55, width=60, height=60,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(left + 75, top - 12, "GLIDE INSTITUTE")

    c.setFillColor(CRIMSON)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left + 75, top - 28, "of Science and Technology")

    c.setFillColor(colors.HexColor("#888888"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(left + 75, top - 44,
                 "P.O Box 71252, Clock Tower, Kampala, Uganda")

    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(left, top - 62, width - left, top - 62)

    # Title
    title_y = height - 145

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, title_y, "CERTIFICATE")

    c.setFillColor(CRIMSON)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(
        width / 2, title_y - 20,
        certificate.get_certificate_type_display().upper()
    )

    # Content
    content = get_certificate_content(certificate)

    y = title_y - 55
    line_gap = 16

    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, y, content["intro_text"])
    y -= 30

    student_name = content["student_name"]
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, y, student_name)
    y -= 14

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    name_w = c.stringWidth(student_name, "Helvetica-Bold", 24)
    c.line(width / 2 - name_w / 2 - 20, y,
           width / 2 + name_w / 2 + 20, y)
    y -= 14

    c.setFillColor(colors.HexColor("#666666"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y, f"Registration No. {content['reg_no']}")
    y -= 24

    c.setFillColor(colors.HexColor("#444444"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, y, content["body_text"])
    y -= line_gap + 6

    if content.get("award_text"):
        c.setFillColor(CRIMSON)
        c.setFont("Helvetica-Bold", 17)
        c.drawCentredString(width / 2, y, content["award_text"])
        y -= line_gap + 8

    if content.get("closing_text"):
        c.setFillColor(colors.HexColor("#444444"))
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y, content["closing_text"])
        y -= line_gap

    c.setFillColor(colors.HexColor("#555555"))
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, y - 4, content["seal_text"])

    # Signatures
    sig_y = 130

    left_cx = width * 0.25
    c.setStrokeColor(colors.HexColor("#555555"))
    c.setLineWidth(0.8)
    c.line(left_cx - 80, sig_y, left_cx + 80, sig_y)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(left_cx, sig_y - 14, content["signature_left_name"])
    c.setFillColor(colors.HexColor("#888888"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(left_cx, sig_y - 26,
                        content["signature_left_role"].upper())

    right_cx = width * 0.75
    c.setStrokeColor(colors.HexColor("#555555"))
    c.line(right_cx - 80, sig_y, right_cx + 80, sig_y)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(right_cx, sig_y - 14, content["signature_right_name"])
    c.setFillColor(colors.HexColor("#888888"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(right_cx, sig_y - 26,
                        content["signature_right_role"].upper())

    _draw_seal(c, width / 2, sig_y + 5, radius=40)

    # Footer
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(60, 58, width - 60, 58)

    c.setFillColor(colors.HexColor("#888888"))
    c.setFont("Helvetica", 8)
    c.drawString(60, 44, "CERTIFICATE NO:")

    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(150, 44, certificate.certificate_number)

    c.setFillColor(colors.HexColor("#888888"))
    c.setFont("Helvetica", 8)
    c.drawRightString(width - 60, 44, "VERIFY AT:")
    c.setFillColor(NAVY)
    c.setFont("Courier-Bold", 8)
    c.drawRightString(width - 130, 44, str(certificate.verification_code))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ==================================================================
# ISSUANCE
# ==================================================================

def issue_certificate(student, certificate_type,
                      issued_by=None, course_unit=None, semester=None,
                      academic_year=None, description=""):
    eligible, reason = check_certificate_eligibility(
        student, certificate_type, course_unit
    )
    if not eligible:
        raise ValueError(reason)

    existing = Certificate.objects.filter(
        student=student,
        certificate_type=certificate_type,
        course_unit=course_unit,
        semester=semester,
        status__in=['draft', 'issued'],
    ).first()
    if existing:
        return existing

    title = {
        'course_completion': (
            f"Certificate of Completion - {course_unit.code}"
            if course_unit else "Certificate of Completion"
        ),
        'program_completion': "Certificate of Program Completion",
        'transcript': "Academic Transcript",
        'merit': "Certificate of Merit",
    }.get(certificate_type, "Certificate")

    snapshot = build_snapshot(student, certificate_type, course_unit)

    certificate = Certificate.objects.create(
        student=student,
        certificate_type=certificate_type,
        course_unit=course_unit,
        semester=semester,
        academic_year=academic_year,
        title=title,
        description=description or title,
        status='issued',
        issued_by=issued_by,
        snapshot_data=snapshot,
    )
    return certificate