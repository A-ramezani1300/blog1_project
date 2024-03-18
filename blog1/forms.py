from django import forms
import re
from .models import Comment, Post, User, Account


# form ticket
class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش')
    )
    message = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=250, required=True)
    email = forms.EmailField()
    phone = forms.CharField(max_length=11, required=True)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("Enter the correct contact number")
            else:
                return phone

    def clean_email(self):
        email = self.cleaned_data['phone']
        if email:
            if not re.match(r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email):
                raise forms.ValidationError("The entered value is not a valid email")
        return email


# form comment
class CommentForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) < 3:
                raise forms.ValidationError("The entered name is shorter than allowed")
            else:
                return name

    class Meta:
        model = Comment
        fields = ['name', 'message']


# form post
class CreatePostForm(forms.ModelForm):
    image1 = forms.ImageField(label='تصویر اول')
    image2 = forms.ImageField(label='تصویر دوم')
    title = forms.CharField(max_length=50, label='عنوان پست')
    description = forms.CharField(widget=forms.Textarea, label='توضیحات پست')
    author = forms.CharField(max_length=50, label='نام نویسنده')

    class Meta:
        model = Post
        fields = ['title', 'description', 'reading_time', 'category']


class SearchForm(forms.Form):
    query = forms.CharField()


# form login
class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=30, widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput, label='Password2')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('پسوردها باهم مطابقت ندارن')
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['date_of_birth', 'bio', 'job', 'photo']


class LogoutForm(forms.Form):
    confirm_logout = forms.BooleanField(label='logout', required=True)
