from decimal import Decimal
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect

from apps.placement.models import OJTPlacement
from apps.time_log.models import TimeLog, ActivityNote


@login_required(login_url='login:login')
def home_view(request):
    """
    Home feature — the student dashboard.
    Displays live OJT progress, hours summary, active placement details,
    and recent activity logs. Allows setup of initial placement and quick time entry.
    """
    profile = getattr(request.user, 'profile', None)
    placement = OJTPlacement.objects.filter(user=request.user).order_by('-created_at').first()

    if request.method == 'POST':
        action = request.POST.get('action', 'save_placement')

        if action == 'save_placement':
            company_name = request.POST.get('company_name', '').strip()
            company_address = request.POST.get('company_address', '').strip()
            supervisor_name = request.POST.get('supervisor_name', '').strip()
            supervisor_email = request.POST.get('supervisor_email', '').strip()
            supervisor_phone = request.POST.get('supervisor_phone', '').strip()
            required_hours_val = request.POST.get('required_hours', '').strip()
            start_date_val = request.POST.get('start_date', '').strip()
            end_date_val = request.POST.get('end_date', '').strip()

            errors = []
            if not company_name:
                errors.append('Company name is required.')
            if not supervisor_name:
                errors.append('Supervisor name is required.')
            if not supervisor_email:
                errors.append('Supervisor email is required.')
            try:
                req_hours = Decimal(required_hours_val)
                if req_hours <= 0:
                    errors.append('Required hours must be greater than zero.')
            except Exception:
                errors.append('Please enter a valid number for required hours.')

            try:
                start_date = datetime.date.fromisoformat(start_date_val)
                end_date = datetime.date.fromisoformat(end_date_val)
                if end_date < start_date:
                    errors.append('End date must be after start date.')
            except Exception:
                errors.append('Please enter valid start and end dates.')

            if errors:
                for err in errors:
                    messages.error(request, err)
                return redirect('home:home')

            if not placement:
                placement = OJTPlacement(user=request.user)

            placement.company_name = company_name
            placement.company_address = company_address
            placement.supervisor_name = supervisor_name
            placement.supervisor_email = supervisor_email
            placement.supervisor_phone = supervisor_phone
            placement.required_hours = req_hours
            placement.start_date = start_date
            placement.end_date = end_date
            placement.save()

            messages.success(request, f"OJT Placement at '{company_name}' updated successfully!")
            return redirect('home:home')

        elif action == 'log_time':
            if not placement:
                messages.error(request, 'Please configure your OJT placement first before logging hours.')
                return redirect('home:home')

            log_date_val = request.POST.get('log_date', '').strip()
            time_in_val = request.POST.get('time_in', '').strip()
            time_out_val = request.POST.get('time_out', '').strip()
            description = request.POST.get('description', '').strip()

            try:
                log_date = datetime.date.fromisoformat(log_date_val)
                t_in = datetime.datetime.strptime(time_in_val, "%H:%M").time()
                t_out = datetime.datetime.strptime(time_out_val, "%H:%M").time()

                dt_in = datetime.datetime.combine(log_date, t_in)
                dt_out = datetime.datetime.combine(log_date, t_out)
                if dt_out <= dt_in:
                    messages.error(request, 'Time out must be after time in.')
                    return redirect('home:home')

                computed = round(Decimal((dt_out - dt_in).total_seconds() / 3600.0), 2)
            except Exception:
                messages.error(request, 'Invalid date or time entered. Please verify.')
                return redirect('home:home')

            time_log = TimeLog.objects.create(
                placement=placement,
                log_date=log_date,
                time_in=t_in,
                time_out=t_out,
                hours_computed=computed,
                status='approved',
            )

            if description:
                ActivityNote.objects.create(time_log=time_log, description=description)

            messages.success(request, f"Successfully logged {computed} hours for {log_date}!")
            return redirect('home:home')

    # Compute metrics if placement exists
    stats = {
        'total_logged': Decimal('0.00'),
        'hours_remaining': Decimal('0.00'),
        'progress_percent': 0.0,
        'recent_logs': [],
        'today': datetime.date.today().isoformat(),
    }

    if placement:
        total = TimeLog.objects.filter(placement=placement).aggregate(total=Sum('hours_computed'))['total'] or Decimal('0.00')
        stats['total_logged'] = total
        stats['hours_remaining'] = max(Decimal('0.00'), placement.required_hours - total)
        if placement.required_hours > 0:
            stats['progress_percent'] = min(100.0, round(float(total / placement.required_hours) * 100, 1))
        stats['recent_logs'] = TimeLog.objects.filter(placement=placement).select_related('activity_note').order_by('-log_date', '-created_at')[:5]

    return render(request, 'home/home.html', {
        'profile': profile,
        'placement': placement,
        'stats': stats,
    })
