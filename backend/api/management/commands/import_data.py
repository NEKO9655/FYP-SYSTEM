import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Profile, Course, FYPProject

class Command(BaseCommand):
    help = 'Imports data from a specified Excel file into the database.'

    def handle(self, *args, **options):
        # --- 清理旧数据 ---
        self.stdout.write("Deleting old data...")
        FYPProject.objects.all().delete()
        User.objects.filter(is_superuser=False).delete() # 删除所有非管理员用户
        Course.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Old data deleted."))

        # --- 读取Excel文件 ---
        file_path = './students_data.xlsx'
        try:
            df = pd.read_excel(file_path)
            # 将NaN值替换为空字符串，防止错误
            df = df.fillna('') 
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"'{file_path}' not found. Please place it in the 'backend' directory."))
            return

        self.stdout.write(f"Importing data from {file_path}...")

        # --- 遍历Excel的每一行并创建数据 ---
        for index, row in df.iterrows():
            # 1. 创建或获取 Course
            course_code = row.get('course_code')
            course = None
            if course_code:
                course, _ = Course.objects.get_or_create(code=course_code, defaults={'name': f"Course {course_code}"})

            # 2. 创建或获取 User 和 Profile
            username = row.get('username')
            if not username:
                continue # 如果没有用户名，跳过这一行

            user, created = User.objects.get_or_create(username=username)
            if created:
                # 为新用户设置一个默认密码，比如 'password123'
                user.set_password('password123')
                user.save()
            
            # 更新或创建 Profile
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'full_name': row.get('full_name', ''),
                    'role': row.get('role', 'student'),
                    'course': course,
                }
            )
            # Django 会自动更新User对象的 email, first_name, last_name (如果它们在 Excel 中)
            user.email = row.get('email', '')
            user.save()

            # 3. 如果是学生，创建 FYPProject
            if row.get('role') == 'student' and row.get('title'):
                # 查找导师、副导师和评审员用户
                supervisor = User.objects.filter(username=row.get('supervisor_username')).first()
                co_supervisor = User.objects.filter(username=row.get('co_supervisor_username')).first()
                examiner = User.objects.filter(username=row.get('examiner_username')).first()

                FYPProject.objects.update_or_create(
                    student=user,
                    defaults={
                        'student_matric_id': row.get('student_matric_id', ''),
                        'title': row.get('title', 'No Title'),
                        'fyp_stage': row.get('fyp_stage', 'FYP1'),
                        'course': course,
                        'supervisor': supervisor,
                        'co_supervisor': co_supervisor,
                        'examiner': examiner,
                    }
                )
        
        self.stdout.write(self.style.SUCCESS("Data import completed successfully!"))