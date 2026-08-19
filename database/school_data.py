"""Small, fake in-memory school dataset for the attendance prototype.

Replace this module with SQLAlchemy repositories in the database phase. No data
in this file is real student information.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import TypedDict


class StudentRecord(TypedDict):
    name: str
    username: str
    class_name: str


STUDENTS: dict[str, StudentRecord] = {
    "rahul": {"name": "Rahul", "username": "rahul", "class_name": "10-A"},
    "priya": {"name": "Priya", "username": "priya", "class_name": "10-A"},
    "aarav": {"name": "Aarav", "username": "aarav", "class_name": "9-B"},
    "ananya": {"name": "Ananya", "username": "ananya", "class_name": "9-B"},
}

PARENT_CHILDREN = {"mrs-sharma": {"rahul"}}
TEACHER_CLASSES = {"mr-patil": {"10-A", "9-B"}}


def _school_days(count: int = 20) -> list[date]:
    """Return recent weekdays in the current calendar month for demo records."""
    today = date.today()
    cursor = today.replace(day=1)
    days: list[date] = []
    while cursor.month == today.month and cursor <= today and len(days) < count:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _make_records() -> dict[str, list[dict[str, str]]]:
    absences = {"rahul": {4, 13}, "priya": {9}, "aarav": {3, 7, 15}, "ananya": {12}}
    subjects = ("Mathematics", "Science", "English", "Social Studies", "Computer Science")
    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for student_key in STUDENTS:
        for index, lesson_date in enumerate(_school_days(), start=1):
            records[student_key].append(
                {
                    "date": lesson_date.isoformat(),
                    "subject": subjects[(index - 1) % len(subjects)],
                    "status": "absent" if index in absences[student_key] else "present",
                }
            )
    return dict(records)


ATTENDANCE_RECORDS = _make_records()


def get_student(key: str) -> StudentRecord | None:
    return STUDENTS.get(key.lower())


def find_student_key(value: str) -> str | None:
    normalized = value.lower().replace(".", "").strip()
    for key, student in STUDENTS.items():
        if key in normalized or student["name"].lower() in normalized:
            return key
    return None


def attendance_report(student_key: str) -> dict[str, object]:
    records = ATTENDANCE_RECORDS.get(student_key, [])
    present = sum(record["status"] == "present" for record in records)
    total = len(records)
    return {
        "student": STUDENTS[student_key],
        "month": date.today().strftime("%B %Y"),
        "present": present,
        "total": total,
        "percentage": round((present / total * 100) if total else 0, 1),
        "records": records,
    }


def class_report(class_name: str) -> dict[str, object]:
    member_keys = [key for key, student in STUDENTS.items() if student["class_name"] == class_name]
    reports = [attendance_report(key) for key in member_keys]
    present = sum(int(report["present"]) for report in reports)
    total = sum(int(report["total"]) for report in reports)
    return {"class_name": class_name, "students": reports, "percentage": round((present / total * 100) if total else 0, 1)}


def school_report() -> dict[str, object]:
    reports = [attendance_report(key) for key in STUDENTS]
    present = sum(int(report["present"]) for report in reports)
    total = sum(int(report["total"]) for report in reports)
    return {"percentage": round((present / total * 100) if total else 0, 1), "student_count": len(reports)}
