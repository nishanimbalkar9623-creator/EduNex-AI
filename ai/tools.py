"""Reserved, backend-owned school tool catalog.

No tool is enabled until a future service implements database access and its own
authorization check. The LLM never receives database credentials or SQL access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from database.school_data import (
    PARENT_CHILDREN,
    TEACHER_CLASSES,
    attendance_report,
    class_report,
    find_student_key,
    get_student,
    school_report,
)


@dataclass(frozen=True)
class SchoolToolSpec:
    name: str
    description: str
    enabled: bool = False


SCHOOL_TOOL_CATALOG = (
    SchoolToolSpec("get_student_attendance", "Retrieve an authenticated student's attendance."),
    SchoolToolSpec("get_child_attendance", "Retrieve an authorized parent's child's attendance."),
    SchoolToolSpec("get_class_attendance", "Retrieve attendance for an authorized class."),
    SchoolToolSpec("mark_attendance", "Record attendance after backend authorization."),
    SchoolToolSpec("correct_attendance", "Correct attendance after backend authorization."),
    SchoolToolSpec("get_school_attendance_summary", "Retrieve principal-authorized school totals."),
)

_ATTENDANCE_TERMS = ("attendance", "absent", "present", "lecture record", "lecture records")


def handle_school_question(user: dict[str, str], message: str) -> str | None:
    """Return an authorized factual attendance reply, or ``None`` for normal AI chat.

    This deterministic backend handler is intentionally placed before the LLM so
    a model cannot invent, query, or bypass access to school data.
    """
    text = message.lower()
    if not any(term in text for term in _ATTENDANCE_TERMS):
        return None

    username, role = user["username"], user["role"]
    requested_student = find_student_key(text)

    if role == "principal" and any(term in text for term in ("overall", "school", "all classes")):
        report = school_report()
        return f"School attendance for {date.today():%B %Y} is {report['percentage']}% across {report['student_count']} demo students."

    if "class" in text and role in {"teacher", "principal"}:
        requested_class = "10-A" if "10" in text else "9-B" if "9" in text else None
        if requested_class is None:
            return "Please tell me which class you want to check, for example 10-A or 9-B."
        if role == "teacher" and requested_class not in TEACHER_CLASSES.get(username, set()):
            return "You are not authorized to view attendance for that class."
        report = class_report(requested_class)
        return f"Class {requested_class} attendance for {date.today():%B %Y} is {report['percentage']}%."

    if role == "student":
        target = username
        if requested_student and requested_student != username:
            return "For privacy, you can only view your own attendance."
    elif role == "parent":
        allowed_children = PARENT_CHILDREN.get(username, set())
        target = requested_student or next(iter(allowed_children), None)
        if target not in allowed_children:
            return "For privacy, you can only view attendance for your own child."
    elif role == "teacher":
        target = requested_student
        if target is None:
            return "Please tell me which student's attendance you want to check."
        student = get_student(target)
        if student is None or student["class_name"] not in TEACHER_CLASSES.get(username, set()):
            return "You are not authorized to view attendance for that student."
    elif role == "principal":
        target = requested_student
        if target is None:
            return "Please name a student, ask for a class such as 10-A, or ask for the overall school attendance."
    else:
        return "Attendance is not available for this account."

    report = attendance_report(target)
    student = report["student"]
    if "lecture record" in text:
        records = report["records"][-5:]
        recent = "; ".join(f"{record['date']} — {record['subject']}: {record['status']}" for record in records)
        return f"Recent lecture records for {student['name']}: {recent}."
    return f"{student['name']}'s attendance for {report['month']} is {report['percentage']}% ({report['present']} of {report['total']} recorded lectures)."
