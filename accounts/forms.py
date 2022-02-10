from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

User = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self, *args,
              **kwargs):
        email = self.cleaned_data.get('email').strip()
        password = self.cleaned_data.get('password').strip()

        if email and password:
            qs = User.objects.filter(email=email)
            if not qs.exists():
                raise forms.ValidationError('Такого пользователя нет!')
            if not check_password(password, qs[0].password):
                # полученый пароль, паролю юзера
                raise forms.ValidationError('Пароль не верный!')
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError('Данный аккаунт отключен')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label='Enter first name',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Enter last name',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Enter email',
                             widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Enter password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Enter your password again',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    country = forms.CharField(label='Enter country',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(label='Enter city',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label='Enter address',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'country', 'city', 'address', 'email',)
        #fields = ('email',)

    def clean_password2(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError('Пароли не совпадают!')
        return data['password2']

class BillingForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'country', 'city', 'address')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'country', 'city', 'address', 'email',)
