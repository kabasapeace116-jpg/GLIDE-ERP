# seed_certs.py  — run with:  python manage.py shell < seed_certs.py
import random
from datetime import timedelta
from django.utils import timezone
from core.models import Student, User
from academics.models import Certificate, CourseUnit
from admissions.models import Semester, AcademicYear

CERT_TYPES = ['course_completion', 'program_completion', 'transcript', 'merit']

students = list(Student.objects.all()[:50])
course_units = list(CourseUnit.objects.all())
semesters = list(Semester.objects.all())
academic_years = list(AcademicYear.objects.all())
issuer = User.objects.filter(is_staff=True).first() or User.objects.first()

if not students:
    print("No students found.")
elif not issuer:
    print("No user found.")
else:
    used = set()
    created = 0
    for _ in range(100):
        if created >= 15:
            break
        student = random.choice(students)
        cert_type = random.choice(CERT_TYPES)
        course_unit = None
        semester = random.choice(semesters) if semesters else None

        if cert_type == 'course_completion':
            if not course_units:
                continue
            course_unit = random.choice(course_units)

        key = (student.pk, cert_type,
               course_unit.pk if course_unit else None,
               semester.pk if semester else None)
        if key in used:
            continue
        used.add(key)

        title = {
            'course_completion': f"Certificate of Completion - {course_unit.code}" if course_unit else "Certificate of Completion",
            'program_completion': "Certificate of Program Completion",
            'transcript': "Academic Transcript",
            'merit': "Certificate of Merit",
        }[cert_type]

        snapshot = {
            "student": {
                "registration_number": student.registration_number,
                "full_name": getattr(student, "full_name", str(student)),
            },
            "certificate_type": cert_type,
            "course_unit": {"code": course_unit.code, "name": course_unit.name} if course_unit else None,
            "issued_at": timezone.now().isoformat(),
        }

        Certificate.objects.create(
            student=student,
            certificate_type=cert_type,
            course_unit=course_unit,
            semester=semester,
            academic_year=random.choice(academic_years) if academic_years else None,
            title=title,
            description=f"{title} — sample.",
            issue_date=(timezone.now() - timedelta(days=random.randint(0, 365))).date(),
            status=random.choices(['issued', 'draft', 'revoked'], weights=[80, 15, 5])[0],
            issued_by=issuer,
            snapshot_data=snapshot,
        )
        created += 1

    print(f"Created {created} certificate(s).")