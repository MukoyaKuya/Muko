from django import forms

from .models import ContactSubmission


class ContactSubmissionForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactSubmission
        fields = ('name', 'email', 'message')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Your name',
                'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-sm text-white placeholder-white/40 outline-none transition-colors focus:border-muko-red focus:bg-white/10 focus:ring-2 focus:ring-muko-red/20',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your email',
                'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-sm text-white placeholder-white/40 outline-none transition-colors focus:border-muko-red focus:bg-white/10 focus:ring-2 focus:ring-muko-red/20',
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Tell me about your project, timeline, and budget if you have one…',
                'rows': 3,
                'class': 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-sm text-white placeholder-white/40 outline-none transition-colors focus:border-muko-red focus:bg-white/10 focus:ring-2 focus:ring-muko-red/20 resize-y min-h-[92px]',
            }),
        }

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise forms.ValidationError('Invalid submission.')
        return value
