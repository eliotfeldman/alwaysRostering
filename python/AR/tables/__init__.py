from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from AR.tables.student_schedule import StudentSchedule
from AR.tables.students import Student
from AR.tables.student_user_text import StudentUserText
from AR.tables.district_teacher import DistrictTeacher
from AR.tables.school_teacher import SchoolTeacher
from AR.tables.gradebook_teacher_section import GradebookTeacherSection
from AR.tables.school import School
from AR.tables.staff_job_roles import StaffJobRole

sa_classes = [
    StudentSchedule,
    Student,
    StudentUserText,
    DistrictTeacher,
    GradebookTeacherSection,
    School,
    StaffJobRole
]