from django import forms
from .models import CustomUser

class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    city = forms.CharField(label='Город', required=False)
    avatar = forms.ImageField(label='Аватар', required=False, widget=forms.ClearableFileInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'city', 'avatar']
        labels = {
            'username': 'Имя пользователя',
            'avatar': 'Аватар',
        }

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'city', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот адрес электронной почты уже зарегистрирован.")
        return email