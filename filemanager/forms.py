import os
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class FileUploadForm(forms.Form):
    file = MultipleFileField(label='انتخاب فایل‌ها')

    def clean_file(self):
        uploaded_files = self.cleaned_data['file']
        valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        for uploaded_file in uploaded_files:
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError('فرمت فایل معتبر نیست. لطفاً فایلی با فرمت‌های jpg، jpeg، png، pdf انتخاب کنید.')
        return uploaded_files

class UserEditForm(forms.ModelForm):
    is_admin = forms.BooleanField(required=False, label='مدیر است')
    is_active = forms.BooleanField(required=False, label='فعال است')
    new_password = forms.CharField(required=False, widget=forms.PasswordInput, label='رمز عبور جدید') # noqa

    class Meta:
        model = User
        fields = ['username', 'email', 'is_admin', 'is_active', 'new_password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superuser = self.cleaned_data['is_admin']
        user.is_staff = self.cleaned_data['is_admin']
        user.is_active = self.cleaned_data['is_active']
        new_password = self.cleaned_data['new_password']
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
