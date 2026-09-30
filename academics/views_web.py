# academics/views_web.py
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse, FileResponse
from django.db import models
from django.views.decorators.http import require_POST

from core.models import Student
from .models import Certificate, CourseUnit
from .services.certificate_service import (
    issue_certificate,
    check_certificate_eligibility,
    generate_certificate_pdf,
    get_certificate_content,
)


def _staff_required(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return getattr(user, "user_type", "") in ("admin", "staff", "lecturer")


# ------------------------------------------------------------------
# LIST
# ------------------------------------------------------------------
@login_required
def certificate_list(request):
    if not _staff_required(request.user):
        return HttpResponseForbidden("Not allowed")

    certificates = Certificate.objects.select_related(
        'student', 'course_unit', 'issued_by'
    ).order_by('-issue_date')

    q = request.GET.get('q', '').strip()
    if q:
        certificates = certificates.filter(
            models.Q(certificate_number__icontains=q) |
            models.Q(student__first_name__icontains=q) |
            models.Q(student__last_name__icontains=q) |
            models.Q(student__registration_number__icontains=q)
        )

    cert_type = request.GET.get('type', '')
    if cert_type:
        certificates = certificates.filter(certificate_type=cert_type)

    return render(request, 'academics/certificates.html', {
        'certificates': certificates,
        'certificate_types': Certificate.CERTIFICATE_TYPES,
        'q': q,
        'selected_type': cert_type,
    })


# ------------------------------------------------------------------
# DETAIL
# ------------------------------------------------------------------
@login_required
def certificate_detail(request, pk):
    if not _staff_required(request.user):
        return HttpResponseForbidden("Not allowed")

    certificate = get_object_or_404(
        Certificate.objects.select_related('student', 'course_unit', 'issued_by'),
        pk=pk,
    )

    content = get_certificate_content(certificate)

    return render(request, 'academics/certificate_detail.html', {
        'certificate': certificate,
        'content': content,
    })


# ------------------------------------------------------------------
# GENERATE
# ------------------------------------------------------------------
@login_required
def certificate_generate(request):
    if not _staff_required(request.user):
        return HttpResponseForbidden("Not allowed")

    students = Student.objects.all().order_by('registration_number')
    course_units = CourseUnit.objects.all().order_by('code')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        cert_type = request.POST.get('certificate_type')
        course_unit_id = request.POST.get('course_unit_id') or None
        description = request.POST.get('description', '')

        student = get_object_or_404(Student, pk=student_id)
        course_unit = (
            get_object_or_404(CourseUnit, pk=course_unit_id)
            if course_unit_id else None
        )

        try:
            certificate = issue_certificate(
                student=student,
                certificate_type=cert_type,
                issued_by=request.user,
                course_unit=course_unit,
                description=description,
            )
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'academics/certificate_generate.html', {
                'students': students,
                'course_units': course_units,
                'certificate_types': Certificate.CERTIFICATE_TYPES,
                'form_data': request.POST,
            })

        messages.success(
            request,
            f"Certificate {certificate.certificate_number} generated."
        )
        return redirect('certificate_detail', pk=certificate.pk)

    form_data = request.GET.dict()
    return render(request, 'academics/certificate_generate.html', {
        'students': students,
        'course_units': course_units,
        'certificate_types': Certificate.CERTIFICATE_TYPES,
        'form_data': form_data,
    })


# ------------------------------------------------------------------
# CHECK ELIGIBILITY (AJAX)
# ------------------------------------------------------------------
@login_required
def certificate_check_eligibility_view(request):
    if not _staff_required(request.user):
        return JsonResponse({'error': 'Not allowed'}, status=403)

    student_id = request.GET.get('student_id')
    cert_type = request.GET.get('certificate_type')
    course_unit_id = request.GET.get('course_unit_id') or None

    student = get_object_or_404(Student, pk=student_id)
    course_unit = (
        get_object_or_404(CourseUnit, pk=course_unit_id)
        if course_unit_id else None
    )

    eligible, reason = check_certificate_eligibility(student, cert_type, course_unit)
    return JsonResponse({'eligible': eligible, 'reason': reason})


# ------------------------------------------------------------------
# DOWNLOAD PDF
# ------------------------------------------------------------------
@login_required
def certificate_download(request, pk):
    if not _staff_required(request.user):
        return HttpResponseForbidden("Not allowed")

    certificate = get_object_or_404(Certificate, pk=pk)
    pdf = generate_certificate_pdf(certificate)

    return FileResponse(
        pdf,
        as_attachment=True,
        filename=f"{certificate.certificate_number}.pdf",
        content_type="application/pdf",
    )


# ------------------------------------------------------------------
# PUBLIC VERIFY (no login)
# ------------------------------------------------------------------
def certificate_verify(request, verification_code):
    certificate = Certificate.objects.filter(
        verification_code=verification_code, status='issued'
    ).first()

    return render(request, 'academics/certificate_verify.html', {
        'certificate': certificate,
        'verification_code': verification_code,
    })


# ------------------------------------------------------------------
# UPDATE CONTENT (AJAX from edit mode on preview page)
# ------------------------------------------------------------------
@login_required
@require_POST
def certificate_update_content(request, pk):
    if not _staff_required(request.user):
        return JsonResponse({'error': 'Not allowed'}, status=403)

    certificate = get_object_or_404(Certificate, pk=pk)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    allowed_keys = {
        'intro_text', 'student_name', 'reg_no', 'body_text',
        'award_text', 'closing_text', 'seal_text',
        'signature_left_name', 'signature_left_role',
        'signature_right_name', 'signature_right_role',
    }

    current = certificate.custom_content or {}
    for key, value in payload.items():
        if key in allowed_keys:
            current[key] = str(value).strip() if value is not None else ""

    certificate.custom_content = current
    certificate.save(update_fields=['custom_content', 'updated_at'])

    return JsonResponse({'ok': True, 'custom_content': current})