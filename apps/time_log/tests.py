import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.placement.models import OJTPlacement
from apps.time_log.models import ActivityNote, TimeLog
from apps.time_log import selectors


class TimeLogJoinAndSubqueryTests(TestCase):
    def setUp(self):
        # Create student 1
        self.user1 = User.objects.create_user(
            username="student_one",
            password="testpassword123",
            first_name="Alice",
            last_name="Guo",
        )
        self.placement1 = OJTPlacement.objects.create(
            user=self.user1,
            company_name="Acme Tech Solutions",
            company_address="123 Tech Park, Pasig City",
            supervisor_name="John Supervisor",
            supervisor_email="john@acme.test",
            required_hours=Decimal("400.00"),
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 6, 30),
        )

        # Create student 2 (for multi-tenant isolation testing)
        self.user2 = User.objects.create_user(
            username="student_two",
            password="testpassword123",
            first_name="Bob",
            last_name="Marley",
        )
        self.placement2 = OJTPlacement.objects.create(
            user=self.user2,
            company_name="Globex Corp",
            company_address="456 Corporate Ave, Makati",
            supervisor_name="Jane Supervisor",
            supervisor_email="jane@globex.test",
            required_hours=Decimal("300.00"),
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 6, 30),
        )

    # ----------------------------------------------------
    # SQL JOIN Tests (Prompt 1)
    # ----------------------------------------------------

    def test_anonymous_redirected_to_login(self):
        """Anonymous access to history or insights redirects to login."""
        res_history = self.client.get(reverse("time_log:history"))
        self.assertEqual(res_history.status_code, 302)
        self.assertIn("/login/", res_history.url)

        res_insights = self.client.get(reverse("time_log:insights"))
        self.assertEqual(res_insights.status_code, 302)
        self.assertIn("/login/", res_insights.url)

    def test_join_user_isolation(self):
        """A user only sees their own logs and related placement/notes."""
        # Create log for user 1
        log1 = TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 1),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(17, 0),
            hours_computed=Decimal("8.00"),
            status="approved",
        )
        ActivityNote.objects.create(time_log=log1, description="Alice note")

        # Create log for user 2
        log2 = TimeLog.objects.create(
            placement=self.placement2,
            log_date=datetime.date(2026, 2, 1),
            time_in=datetime.time(9, 0),
            time_out=datetime.time(18, 0),
            hours_computed=Decimal("8.00"),
            status="approved",
        )
        ActivityNote.objects.create(time_log=log2, description="Bob secret note")

        # Check selector for user1
        qs1 = selectors.logs_with_placement_and_note(self.user1)
        self.assertEqual(qs1.count(), 1)
        self.assertEqual(qs1.first().placement.company_name, "Acme Tech Solutions")
        self.assertEqual(qs1.first().activity_note.description, "Alice note")

        # Check view for user1
        self.client.force_login(self.user1)
        resp = self.client.get(reverse("time_log:history"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Acme Tech Solutions")
        self.assertContains(resp, "Alice note")
        self.assertNotContains(resp, "Globex Corp")
        self.assertNotContains(resp, "Bob secret note")

    def test_join_note_and_missing_note(self):
        """Logs with notes display the description; logs without notes display 'No note'."""
        log_with_note = TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 2),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(17, 0),
            hours_computed=Decimal("8.00"),
            status="approved",
        )
        ActivityNote.objects.create(time_log=log_with_note, description="Created database migrations")

        log_without_note = TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 3),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(17, 0),
            hours_computed=Decimal("8.00"),
            status="pending",
        )

        self.client.force_login(self.user1)
        resp = self.client.get(reverse("time_log:history"))
        self.assertContains(resp, "Created database migrations")
        self.assertContains(resp, "No note")

    def test_join_single_query_no_n_plus_one(self):
        """Iterating through 10 logs with their placement and notes executes exactly 1 query."""
        for day in range(1, 11):
            tl = TimeLog.objects.create(
                placement=self.placement1,
                log_date=datetime.date(2026, 2, day),
                time_in=datetime.time(8, 0),
                time_out=datetime.time(17, 0),
                hours_computed=Decimal("8.00"),
                status="approved",
            )
            if day % 2 == 0:
                ActivityNote.objects.create(time_log=tl, description=f"Note for day {day}")

        with self.assertNumQueries(1):
            qs = selectors.logs_with_placement_and_note(self.user1)
            for log in qs:
                # Accessing related placement and activity_note should not fire new queries
                _ = log.placement.company_name
                _ = log.placement.supervisor_name
                _ = getattr(log, 'activity_note', None)

    def test_status_filter(self):
        """Status filter filters logs correctly; invalid filter is ignored."""
        TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 1),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(17, 0),
            hours_computed=Decimal("8.00"),
            status="pending",
        )
        TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 2),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(17, 0),
            hours_computed=Decimal("8.00"),
            status="approved",
        )

        self.client.force_login(self.user1)

        # Filter pending
        resp = self.client.get(reverse("time_log:history") + "?status=pending")
        self.assertEqual(len(resp.context["page_obj"]), 1)
        self.assertEqual(resp.context["page_obj"][0].status, "pending")

        # Filter approved
        resp = self.client.get(reverse("time_log:history") + "?status=approved")
        self.assertEqual(len(resp.context["page_obj"]), 1)
        self.assertEqual(resp.context["page_obj"][0].status, "approved")

        # Invalid filter returns all
        resp = self.client.get(reverse("time_log:history") + "?status=hacked")
        self.assertEqual(len(resp.context["page_obj"]), 2)

    # ----------------------------------------------------
    # SQL SUBQUERY Tests (Prompt 3 & 3B)
    # ----------------------------------------------------

    def test_subquery_above_average_logs(self):
        """
        With logs of 4, 8, 8, 8, 12 hours (avg 8.00),
        only the 12h log is returned (strictly greater than average).
        """
        hours_list = [Decimal("4.00"), Decimal("8.00"), Decimal("8.00"), Decimal("8.00"), Decimal("12.00")]
        for idx, h in enumerate(hours_list, start=1):
            TimeLog.objects.create(
                placement=self.placement1,
                log_date=datetime.date(2026, 2, idx),
                time_in=datetime.time(8, 0),
                time_out=datetime.time(17, 0),
                hours_computed=h,
                status="approved",
            )

        avg = selectors.average_hours(self.user1)
        self.assertEqual(avg, Decimal("8.00"))

        above = list(selectors.above_average_logs(self.user1))
        self.assertEqual(len(above), 1)
        self.assertEqual(above[0].hours_computed, Decimal("12.00"))

    def test_subquery_user_isolation(self):
        """User 2 logs with high hours do not skew User 1's average or results."""
        # User 1 has log of 6 and 8 (avg = 7.00)
        TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 1),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(14, 0),
            hours_computed=Decimal("6.00"),
            status="approved",
        )
        TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 2),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(16, 0),
            hours_computed=Decimal("8.00"),
            status="approved",
        )

        # User 2 logs 50 hours
        TimeLog.objects.create(
            placement=self.placement2,
            log_date=datetime.date(2026, 2, 1),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(20, 0),
            hours_computed=Decimal("50.00"),
            status="approved",
        )

        avg1 = selectors.average_hours(self.user1)
        self.assertEqual(avg1, Decimal("7.00"))

        above1 = list(selectors.above_average_logs(self.user1))
        self.assertEqual(len(above1), 1)
        self.assertEqual(above1[0].hours_computed, Decimal("8.00"))

    def test_subquery_zero_hours_ignored(self):
        """Logs with 0.00 hours are ignored in the average computation."""
        TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 1),
            time_in=datetime.time(8, 0),
            hours_computed=Decimal("0.00"),
            status="pending",
        )
        TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 2),
            time_in=datetime.time(8, 0),
            hours_computed=Decimal("10.00"),
            status="approved",
        )

        avg = selectors.average_hours(self.user1)
        self.assertEqual(avg, Decimal("10.00"))

    def test_subquery_no_logs_handled(self):
        """User with no logs loads insights without error."""
        self.client.force_login(self.user1)
        resp = self.client.get(reverse("time_log:insights"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No days above your average yet")

    def test_subquery_missing_notes(self):
        """Task 3B: logs_missing_notes returns only logs that do not have an activity note."""
        log_with_note = TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 1),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(17, 0),
            hours_computed=Decimal("8.00"),
            status="approved",
        )
        ActivityNote.objects.create(time_log=log_with_note, description="Done")

        log_without_note = TimeLog.objects.create(
            placement=self.placement1,
            log_date=datetime.date(2026, 2, 2),
            time_in=datetime.time(8, 0),
            time_out=datetime.time(17, 0),
            hours_computed=Decimal("8.00"),
            status="pending",
        )

        missing = list(selectors.logs_missing_notes(self.user1))
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].id, log_without_note.id)
