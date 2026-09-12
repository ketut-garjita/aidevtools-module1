from django import forms
from .models import Chore


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ['title', 'description', 'assigned_member', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition',
                'placeholder': 'e.g., Take out recycling bin'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition',
                'placeholder': 'Optional details or instructions...',
                'rows': 3
            }),
            'assigned_member': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition',
                'placeholder': 'e.g., Alex, Sam, Jordan'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition bg-white'
            }),
        }
