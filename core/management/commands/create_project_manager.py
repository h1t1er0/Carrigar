from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import ProjectManager

class Command(BaseCommand):
    help = 'Create a project manager user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the project manager')
        parser.add_argument('--email', type=str, help='Email for the project manager')
        parser.add_argument('--password', type=str, help='Password for the project manager')
        parser.add_argument('--employee_id', type=str, help='Employee ID for the project manager')
        parser.add_argument('--first_name', type=str, help='First name')
        parser.add_argument('--last_name', type=str, help='Last name')

    def handle(self, *args, **options):
        username = options['username'] or 'pm_admin'
        email = options['email'] or 'pm@carrigar.com'
        password = options['password'] or 'carrigar123'
        employee_id = options['employee_id'] or 'PM001'
        first_name = options['first_name'] or 'Project'
        last_name = options['last_name'] or 'Manager'

        # Create user if doesn't exist
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': True,
                'is_active': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))

        # Create project manager profile if doesn't exist
        pm, pm_created = ProjectManager.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': employee_id,
                'department': 'Operations',
                'is_active': True,
            }
        )

        if pm_created:
            self.stdout.write(self.style.SUCCESS(f'Created ProjectManager profile for {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'ProjectManager profile for {username} already exists'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nProject Manager created successfully!\n'
                f'Username: {username}\n'
                f'Email: {email}\n'
                f'Password: {password}\n'
                f'Employee ID: {employee_id}\n'
                f'Access the CRM at: http://127.0.0.1:8000/crm/\n'
            )
        )
