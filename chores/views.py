from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Chore
from .forms import ChoreForm


def chore_list(request):
    """Display all household chores and their status."""
    status_filter = request.GET.get('status', '')
    member_filter = request.GET.get('member', '')

    chores = Chore.objects.all()

    if status_filter:
        chores = chores.filter(status=status_filter)
    if member_filter:
        chores = chores.filter(assigned_member__icontains=member_filter)

    total_count = Chore.objects.count()
    pending_count = Chore.objects.filter(status=Chore.STATUS_PENDING).count()
    completed_count = Chore.objects.filter(status=Chore.STATUS_COMPLETED).count()

    # Get distinct assigned members for filter dropdown
    members = (
        Chore.objects.exclude(assigned_member='')
        .values_list('assigned_member', flat=True)
        .distinct()
    )

    today = timezone.now().date()

    context = {
        'chores': chores,
        'total_count': total_count,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'members': members,
        'current_status': status_filter,
        'current_member': member_filter,
        'today': today,
    }
    return render(request, 'chores/chore_list.html', context)


def chore_create(request):
    """Allow users to create new chores."""
    if request.method == 'POST':
        form = ChoreForm(request.POST)
        if form.is_valid():
            chore = form.save(commit=False)
            if chore.status == Chore.STATUS_COMPLETED and not chore.completion_date:
                chore.completion_date = timezone.now().date()
            chore.save()
            messages.success(request, f'Chore "{chore.title}" created successfully!')
            return redirect('chores:list')
    else:
        form = ChoreForm()

    return render(request, 'chores/chore_form.html', {'form': form})


def chore_complete(request, pk):
    """Allow users to mark chores as completed."""
    chore = get_object_or_404(Chore, pk=pk)
    if request.method == 'POST':
        chore.mark_completed()
        messages.success(request, f'Chore "{chore.title}" marked as completed!')
    return redirect('chores:list')


def chore_delete(request, pk):
    """Allow users to delete a chore."""
    chore = get_object_or_404(Chore, pk=pk)
    if request.method == 'POST':
        title = chore.title
        chore.delete()
        messages.success(request, f'Chore "{title}" was deleted.')
    return redirect('chores:list')
