from decimal import Decimal
from django.db.models import Avg, Subquery
from .models import ActivityNote, TimeLog


def logs_with_placement_and_note(user):
    """
    JOIN time_log with ojt_placement and activity_note in ONE query.

    select_related follows the ForeignKey ('placement') and the reverse OneToOne
    ('activity_note') using a SQL JOIN so no extra queries are run per row (avoids N+1).
    - Placement is joined via INNER JOIN because placement_id is a non-null foreign key.
    - ActivityNote is joined via LEFT OUTER JOIN because a time log entry may not have
      an activity note attached yet.
    """
    return (
        TimeLog.objects
        .select_related('placement', 'activity_note')
        .filter(placement__user=user)
        .order_by('-log_date', '-time_in')
    )


def above_average_logs(user):
    """
    Logs with more hours than this user's average day (SUBQUERY).

    INNER query: Computes the scalar average of hours_computed for this specific user's
                 non-zero time logs.
    OUTER query: Filters time_log rows for this user where hours_computed is strictly greater
                 than that scalar subquery result.
    """
    own_logs = TimeLog.objects.filter(placement__user=user, hours_computed__gt=0)
    avg_hours = (
        own_logs
        .values('placement__user')
        .annotate(avg=Avg('hours_computed'))
        .values('avg')[:1]
    )
    return (
        own_logs
        .select_related('placement')
        .filter(hours_computed__gt=Subquery(avg_hours))
        .order_by('-hours_computed', '-log_date')
    )


def average_hours(user):
    """
    Returns the user's average logged hours per day as a Decimal/float,
    or None if no non-zero logs exist (used for stat displays).
    """
    return (
        TimeLog.objects
        .filter(placement__user=user, hours_computed__gt=0)
        .aggregate(avg=Avg('hours_computed'))['avg']
    )


def logs_missing_notes(user):
    """
    Logs whose id is NOT in the set of time_log_ids that have an activity note (SUBQUERY).

    INNER query: SELECT time_log_id FROM activity_note.
    OUTER query: SELECT ... FROM time_log WHERE id NOT IN (SELECT time_log_id FROM activity_note).
    """
    noted_ids = ActivityNote.objects.values('time_log_id')
    return (
        TimeLog.objects
        .filter(placement__user=user)
        .exclude(id__in=Subquery(noted_ids))
        .select_related('placement')
        .order_by('-log_date', '-time_in')
    )
