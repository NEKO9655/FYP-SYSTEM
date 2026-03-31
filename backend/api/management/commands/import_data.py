# api/management/commands/import_data.py
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Profile, Course, FYPProject, TimetableSlot

class Command(BaseCommand):
    help = 'Complete and robust data import: Full Name, Matric ID, Co-Supervisor included'

    def handle(self, *args, **kwargs):
        # 1. 准备阶段：加载并清洗数据
        try:
            df_main = pd.read_excel('students_data.xlsx')
            # 将所有 Excel 的空值转换为 None，防止出现 NaN 报错
            df_main = df_main.replace({np.nan: None})
            self.stdout.write("Processing students_data.xlsx...")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical: Could not read students_data.xlsx: {e}"))
            return

        # --- 步骤 1: 全局用户注册 (确保所有引用的账号都存在) ---
        self.stdout.write("Step 1: Registering all unique User accounts...")
        # 收集所有可能出现的用户名（学生、主导师、副导师）
        all_potential_usernames = set()
        
        cols_to_check = ['username', 'supervisor_username', 'co_supervisor_username']
        for col in cols_to_check:
            if col in df_main.columns:
                # 过滤掉 None 和空字符串
                valid_names = df_main[col].dropna().unique()
                all_potential_usernames.update([str(n).strip() for n in valid_names if str(n).strip()])

        for uname in all_potential_usernames:
            if uname.lower() == 'none' or not uname: continue
            user, created = User.objects.get_or_create(username=uname)
            if created:
                user.set_password('wow12345')
                user.save()

        # --- 步骤 2: 完善 Profile (导入 Full Name, Course, Role) ---
        self.stdout.write("Step 2: Updating Profiles (Full Name & Roles)...")
        for _, row in df_main.iterrows():
            uname = str(row.get('username', '')).strip()
            # 跳过空行或无效行
            if not uname or uname.lower() == 'none': continue

            try:
                user = User.objects.get(username=uname)
                
                # 处理课程
                course_code = str(row.get('course_code', 'General')).strip()
                course, _ = Course.objects.get_or_create(
                    code=course_code,
                    defaults={'name': course_code}
                )
                
                # 导入 Full Name
                Profile.objects.update_or_create(
                    user=user,
                    defaults={
                        'full_name': row.get('full_name'), # 关键：导入全名
                        'role': str(row.get('role', 'student')).lower(),
                        'course': course,
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping profile for {uname}: {e}"))

        # --- 步骤 3: 建立项目关系 (导入 Matric ID & Co-Supervisor) ---
        self.stdout.write("Step 3: Creating Projects and linking Supervisors...")
        for _, row in df_main.iterrows():
            uname = str(row.get('username', '')).strip()
            title = row.get('project_title')
            
            # 如果没有学生账号或没有项目标题，跳过
            if not uname or uname.lower() == 'none' or not title: continue

            try:
                student_user = User.objects.get(username=uname)
                
                # 获取主导师
                super_name = str(row.get('supervisor_username', '')).strip()
                super_user = User.objects.get(username=super_name) if super_name and super_name.lower() != 'none' else None
                
                # 获取副导师 (Co-Supervisor)
                co_super_name = str(row.get('co_supervisor_username', '')).strip()
                co_super_user = User.objects.get(username=co_super_name) if co_super_name and co_super_name.lower() != 'none' else None

                # 存入项目资料
                FYPProject.objects.update_or_create(
                    title=str(title).strip(),
                    defaults={
                        'student': student_user,
                        'student_matric_id': row.get('student_matric_id'), # 关键：导入学号
                        'supervisor': super_user,
                        'co_supervisor': co_super_user, # 关键：导入副导师
                        'fyp_stage': row.get('fyp_stage', 'FYP1'),
                    }
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to create project '{title}': {e}"))

        self.stdout.write(self.style.SUCCESS("Phase 1 & 2 Complete!"))

        # --- 步骤 4: 导入时间表和考官 (来自 slots_data.xlsx) ---
        try:
            df_slots = pd.read_excel('slots_data.xlsx')
            df_slots = df_slots.replace({np.nan: None})
            self.stdout.write("Step 4: Importing Slots and Examiners from slots_data.xlsx...")
            
            for _, row in df_slots.iterrows():
                p_title = str(row.get('project_title', '')).strip()
                if not p_title or p_title.lower() == 'none': continue
                
                try:
                    project = FYPProject.objects.get(title=p_title)
                    
                    # 导入考官 (Examiner)
                    ex_name = str(row.get('examiner_usernames', '')).strip()
                    if ex_name and ex_name.lower() != 'none':
                        ex_user, _ = User.objects.get_or_create(username=ex_name)
                        # 确保考官也有 Profile
                        Profile.objects.get_or_create(user=ex_user, defaults={'role': 'lecturer'})
                        project.examiner = ex_user
                        project.save()

                    # 导入具体的 Slot
                    if row.get('start_time'):
                        TimetableSlot.objects.update_or_create(
                            project=project,
                            defaults={
                                'start_time': row['start_time'],
                                'end_time': row['end_time'],
                                'venue': row['venue'],
                            }
                        )
                except FYPProject.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Slot Error: Project '{p_title}' not found in database."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error in slot row: {e}"))

            self.stdout.write(self.style.SUCCESS('--- ALL DATA IMPORTED SUCCESSFULLY ---'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Phase 4 Error: {e}"))