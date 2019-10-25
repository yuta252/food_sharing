from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm

from .models import User, Message, Friend, Good, Comment

# User signup auth
class SignupForm(UserCreationForm):
    """ユーザー登録用フォーム"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('userid', 'username', 'email', 'thumbnail', 'self_intro')
        widgets = {
            'userid': forms.TextInput(attrs={'class':'userid-create-form'}),
            'username': forms.TextInput(attrs={'class':'username-create-form'}),
            'email': forms.EmailInput(attrs={'class':'email-create-form'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        # 仮登録で操作が停止している場合、再度登録するときに仮登録のデータを削除
        User.objects.filter(email=email, is_active=False).delete()
        return email

# User edit form
class UserEditForm(forms.ModelForm):
    """ユーザー情報編集用フォーム"""
    class Meta:
        model = User
        fields = ('username', 'email', 'thumbnail', 'self_intro')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# Password change
class MyPasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# Password reset form
class MyPasswordResetForm(PasswordResetForm):
    """パスワード忘れた時のフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class MySetPasswordForm(SetPasswordForm):
    """パスワード再設定用フォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# Emal change form
class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

# Login form
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

# MessageForm
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('post_pic', 'content')
        widgets = {
            'content': forms.Textarea(attrs={'id':'comment-input','class':'post-form', 'placeholder':"コメントを入力", 'aria-label': "", 'aria-describedby':"basic-addon1"})
        }

# CommentForm
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('reply',)
        widgets = {
            'reply': forms.Textarea(attrs={'id':'reply-input', 'class':'reply-form', 'placeholder':"コメントを入力"})
        }

class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = '__all__'

class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = '__all__'

# search form
class SearchForm(forms.Form):
    search = forms.CharField(max_length=100)

# Post form
class PostForm(forms.Form):
    content = forms.CharField(max_length=150, widget=forms.Textarea)