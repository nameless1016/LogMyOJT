from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import render

from . import selectors


@login_required(login_url='login:login')
def log_history(request):
    """
    Time Log History page (SQL JOIN demonstration).
    Lists time logs with placement (company, supervisor) and activity notes in a single query.
    """
    status_filter = request.GET.get('status', '').strip().lower()
    allowed_statuses = {'pending', 'approved', 'rejected'}

    qs = selectors.logs_with_placement_and_note(request.user)

    if status_filter in allowed_statuses:
        qs = qs.filter(status=status_filter)

    total_hours = qs.aggregate(total=Sum('hours_computed'))['total'] or Decimal('0.00')

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    profile = getattr(request.user, 'profile', None)

    context = {
        'page_obj': page_obj,
        'total_hours': total_hours,
        'selected_status': status_filter if status_filter in allowed_statuses else '',
        'profile': profile,
    }
    return render(request, 'time_log/log_history.html', context)


@login_required(login_url='login:login')
def insights(request):
    """
    Time Log Insights page (SQL SUBQUERY demonstration).
    Shows days where logged hours exceed the student's own average hours,
    and logs missing an activity note.
    """
    avg_hours = selectors.average_hours(request.user)
    above_logs = list(selectors.above_average_logs(request.user))

    # Calculate difference above average for display
    if avg_hours:
        avg_decimal = Decimal(str(avg_hours))
        for log in above_logs:
            log.hours_diff = round(log.hours_computed - avg_decimal, 2)
    else:
        for log in above_logs:
            log.hours_diff = Decimal('0.00')

    missing_notes = selectors.logs_missing_notes(request.user)
    profile = getattr(request.user, 'profile', None)

    context = {
        'avg_hours': round(avg_hours, 2) if avg_hours is not None else None,
        'above_average_logs': above_logs,
        'above_count': len(above_logs),
        'missing_notes_logs': missing_notes,
        'missing_count': missing_notes.count(),
        'profile': profile,
    }
    return render(request, 'time_log/insights.html', context)
