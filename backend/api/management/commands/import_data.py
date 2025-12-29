# --- File: backend/api/management/commands/import_data.py (FINAL DEBUGGING VERSION) ---

import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Profile, Course, FYPProject, TimetableSlot

class Command(BaseCommand):
    help = 'Imports data from Excel files for users, projects, and slots.'

    def handle(self, *args, **options):
        # --- Clean up old data ---
        self.stdout.write("Deleting old data...")
        TimetableSlot.objects.all().delete()
        FYPProject.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Course.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Old data deleted."))

        # --- Read the main data file ---
        students_file_path = 'students_data.xlsx'
        try:
            df = pd.read_excel(students_file_path).fillna('')
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"CRITICAL: '{students_file_path}' not found. Aborting."))
            return

        # --- PASS 1: Create all Courses and Users ---
        self.stdout.write("Starting Pass 1: Creating Courses and Users...")
        for index, row in df.iterrows():
            course = None
            if row.get('course_code'):
                course, _ = Course.objects.get_or_create(code=row.get('course_code'), defaults={'name': f"Course for {row.get('course_code')}"})
            username = str(row.get('username', '')).strip()
            if username:
                user, created = User.objects.get_or_create(username=username)
                if created: user.set_password('password123');
                user.email = str(row.get('email', '')).strip()
                user.save()
                Profile.objects.update_or_create(user=user, defaults={
                    'full_name': str(row.get('full_name', '')).strip(),
                    'role': str(row.get('role', 'student')).strip().lower(),
                    'course': course
                })
        self.stdout.write(self.style.SUCCESS("Pass 1 completed."))

        # --- PASS 2: Create FYPProjects with DEBUGGING ---
        self.stdout.write("Starting Pass 2: Creating and linking FYP Projects...")
        project_titles_created = [] # A list to track successfully created project titles
        for index, row in df.iterrows():
            role = str(row.get('role', '')).strip().lower()
            project_title = str(row.get('project_title', '')).strip()

            if role == 'student' and project_title:
                try:
                    student_user = User.objects.get(username=row.get('username'))
                    supervisor = User.objects.filter(username=row.get('supervisor_username')).first()
                    co_supervisor = User.objects.filter(username=row.get('co_supervisor_username')).first()
                    examiner = User.objects.filter(username=row.get('examiner_username')).first()
                    course = Course.objects.filter(code=row.get('course_code')).first()
                    
                    project, created = FYPProject.objects.get_or_create(
                        student=student_user,
                        defaults={
                            'title': project_title,
                            'student_matric_id': str(row.get('student_matric_id', '')).strip(),
                            'fyp_stage': str(row.get('fyp_stage', 'FYP1')).strip(),
                            'course': course,
                            'supervisor': supervisor,
                            'co_supervisor': co_supervisor,
                            'examiner': examiner,
                        }
                    )
                    if created:
                        project_titles_created.append(project.title) # Record the title

                except User.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"Pass 2 Warning: Skipping project for non-existent user '{row.get('username')}'."))
        
        self.stdout.write(self.style.SUCCESS("Pass 2 completed."))
        
        # --- CRUCIAL DEBUG OUTPUT ---
        self.stdout.write("--- DEBUG: Titles created in Pass 2 ---")
        if project_titles_created:
            for title in project_titles_created:
                self.stdout.write(f"- '{title}'")
        else:
            self.stdout.write(self.style.WARNING("!!! NO PROJECTS WERE CREATED IN PASS 2 !!! Check 'students_data.xlsx' for correct headers ('project_title', 'role') and content."))
        self.stdout.write("------------------------------------")
        
        # --- PASS 3: Import Timetable Slots ---
        self.stdout.write("Starting Pass 3: Importing Timetable Slots...")
        slots_file_path = 'slots_data.xlsx'
        try:
            slots_df = pd.read_excel(slots_file_path).fillna('')
            for index, row in slots_df.iterrows():
                project_title_to_find = str(row.get('project_title', '')).strip()
                project = FYPProject.objects.filter(title=project_title_to_find).first()
                
                if not project:
                    self.stderr.write(self.style.WARNING(f"Pass 3 Warning: Skipping slot for non-existent project: '{project_title_to_find}'"))
                    continue

                slot = TimetableSlot.objects.create(
                    project=project,
                    start_time=row.get('start_time'),
                    end_time=row.get('end_time'),
                    venue=str(row.get('venue', '')).strip()
                )

                examiner_names_str = str(row.get('examiner_usernames', ''))
                examiner_names = [name.strip() for name in examiner_names_str.split(',') if name.strip()]
                if examiner_names:
                    examiners = User.objects.filter(username__in=examiner_names)
                    slot.examiners.set(examiners)
        
        except FileNotFoundError:
            self.stdout.write(self.style.NOTICE(f"'{slots_file_path}' not found, skipping Pass 3."))
        
        self.stdout.write(self.style.SUCCESS("Data import finished!"))