import datetime
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.placement.models import OJTPlacement
from apps.time_log.models import ActivityNote, TimeLog


class Command(BaseCommand):
    help = "Seeds 15 realistic demo time logs (with varied hours, statuses, and notes) for school activity demonstration."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username of the student")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Refusing to seed demo data in production mode (DEBUG=False).")

        username = options["username"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User with username '{username}' does not exist.")

        placement = OJTPlacement.objects.filter(user=user).order_by('-created_at').first()
        if not placement:
            raise CommandError(
                f"User '{username}' does not have an OJTPlacement registered yet. "
                "Please register an internship placement on the dashboard first."
            )

        # Candidate hours and statuses to provide a realistic distribution
        # Some are short (4, 6), standard (8), and heavy (9, 10, 12) to demonstrate above-average subquery
        demo_specs = [
            (Decimal("8.00"), "08:00", "17:00", "approved", "Conducted code review for authentication module and updated PR comments."),
            (Decimal("7.50"), "08:30", "17:00", "approved", "Configured Supabase database tables and wrote initial ORM models."),
            (Decimal("8.00"), "08:00", "17:00", "approved", "Daily standup meeting and implemented password reset email workflow."),
            (Decimal("9.00"), "08:00", "18:00", "approved", "Assisted senior engineer with database query optimization and indexing."),
            (Decimal("4.00"), "08:00", "12:00", "approved", "Half-day schedule due to university midterm examination."),
            (Decimal("8.00"), "08:00", "17:00", "approved", "Fixed CSS styling issues on mobile viewports for the student dashboard."),
            (Decimal("10.00"), "08:00", "19:00", "approved", "Sprint release preparation and load testing on backend API endpoints."),
            (Decimal("8.00"), "08:00", "17:00", "approved", "Researched SQL JOIN and Subquery operations in Django ORM."),
            (Decimal("6.00"), "09:00", "16:00", "approved", "Documented REST API specifications in OpenAPI format."),
            (Decimal("12.00"), "08:00", "21:00", "approved", "Overtime deployment shift for version 1.2 system migration."),
            (Decimal("8.00"), "08:00", "17:00", "pending", None),  # Missing note
            (Decimal("8.50"), "08:00", "17:30", "pending", "Implemented time log export functionality to CSV format."),
            (Decimal("8.00"), "08:00", "17:00", "pending", None),  # Missing note
            (Decimal("8.00"), "08:00", "17:00", "rejected", None),  # Missing note & rejected
            (Decimal("7.00"), "08:30", "16:30", "pending", None),  # Missing note
        ]

        # Find available past weekdays within placement range
        today = timezone.localdate()
        target_date = min(today, placement.end_date)
        
        # Collect existing dates for this placement to avoid duplicates
        existing_dates = set(TimeLog.objects.filter(placement=placement).values_list('log_date', flat=True))

        created_logs = 0
        created_notes = 0

        current_cursor = target_date
        spec_index = 0

        while spec_index < len(demo_specs) and current_cursor >= placement.start_date:
            # Check if current_cursor is a weekday (Monday=0 ... Friday=4)
            if current_cursor.weekday() < 5 and current_cursor not in existing_dates:
                hours, t_in, t_out, status, note_text = demo_specs[spec_index]
                
                time_in_obj = datetime.time.fromisoformat(t_in)
                time_out_obj = datetime.time.fromisoformat(t_out)

                log = TimeLog.objects.create(
                    placement=placement,
                    log_date=current_cursor,
                    time_in=time_in_obj,
                    time_out=time_out_obj,
                    hours_computed=hours,
                    status=status,
                )
                created_logs += 1

                if note_text:
                    ActivityNote.objects.create(time_log=log, description=note_text)
                    created_notes += 1

                existing_dates.add(current_cursor)
                spec_index += 1

            current_cursor -= datetime.timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded {created_logs} time logs ({created_notes} with activity notes) for user '{username}'."
            )
        )
