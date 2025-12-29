# --- File: backend/api/management/commands/import_data.py (FINAL UPGRADED VERSION) ---

import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
# --- 1. Import TimetableSlot ---
from api.models import Profile, Course, FYPProject, TimetableSlot

class Command(BaseCommand):
    help = 'Imports data from Excel files for users, projects, and timetable slots.'

    def handle(self, *args, **options):
        # --- Clean up old data ---
        self.stdout.write("Deleting old data...")
        TimetableSlot.objects.all().delete() # Also delete old slots
        FYPProject.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Course.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Old data deleted."))

        # --- PASS 1 & 2: Import Users and Projects (Your existing logic) ---
        file_path = 'students_data.xlsx'
        try:
            df = pd.read_excel(file_path).fillna('')
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"'{file_path}' not found."))
            return

        self.stdout.write("Starting Pass 1: Creating Courses and Users...")
        for index, row in df.iterrows():
            course = None
            if row.get('course_code'):
                course, _ = Course.objects.get_or_create(code=row.get('course_code'), defaults={'name': f"Course {row.get('course_code')}"})
            username = row.get('username')
            if username:
                user, created = User.objects.get_or_create(username=username)
                if created: user.set_password('password123'); user.save()
                user.email = row.get('email', '')
                user.save()
                Profile.objects.update_or_create(user=user, defaults={'full_name': row.get('full_name', ''), 'role': row.get('role', 'student'), 'course': course})
        self.stdout.write(self.style.SUCCESS("Pass 1 completed."))

        self.stdout.write("Starting Pass 2: Creating and linking FYP Projects...")
        for index, row in df.iterrows():
            if row.get('role') == 'student' and row.get('title'):
                try:
                    student_user = User.objects.get(username=row.get('username'))
                    supervisor = User.objects.filter(username=row.get('supervisor_username')).first()
                    co_supervisor = User.objects.filter(username=row.get('co_supervisor_username')).first()
                    examiner = User.objects.filter(username=row.get('examiner_username')).first()
                    course = Course.objects.filter(code=row.get('course_code')).first()
                    FYPProject.objects.create(student=student_user, student_matric_id=row.get('student_matric_id', ''), title=row.get('title', 'No Title'), fyp_stage=row.get('fyp_stage', 'FYP1'), course=course, supervisor=supervisor, co_supervisor=co_supervisor, examiner=examiner)
                except User.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"Skipping project for non-existent user: {row.get('username')}"))
        self.stdout.write(self.style.SUCCESS("Pass 2 completed."))


        # --- 2. 【NEW】PASS 3: Import Timetable Slots ---
        self.stdout.write("Starting Pass 3: Importing Timetable Slots...")
        slots_file_path = 'slots_data.xlsx'
        try:
            slots_df = pd.read_excel(slots_file_path).fillna('')

            for index, row in slots_df.iterrows():
                # Find the project by its title
                project = FYPProject.objects.filter(title=row.get('project_title')).first()
                if not project:
                    self.stderr.write(self.style.WARNING(f"Skipping slot for non-existent project: '{row.get('project_title')}'"))
                    continue

                # Create the TimetableSlot instance
                slot = TimetableSlot.objects.create(
                    project=project,
                    start_time=row.get('start_time'),
                    end_time=row.get('end_time'),
                    venue=row.get('venue', '')
                )

                # Handle multiple examiners (ManyToMany field)
                examiner_names_str = str(row.get('examiner_usernames', ''))
                examiner_names = [name.strip() for name in examiner_names_str.split(',') if name.strip()]
                if examiner_names:
                    examiners = User.objects.filter(username__in=examiner_names)
                    slot.examiners.set(examiners) # Use .set() for ManyToMany fields
        
        except FileNotFoundError:
            # This is not an error, just a notice if the file doesn't exist.
            self.stdout.write(self.style.NOTICE(f"'{slots_file_path}' not found, skipping slot import."))
        
        self.stdout.write(self.style.SUCCESS("Pass 3 completed. Data import finished!"))