from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, Message, Friend, Good, Share

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)

class MyUserAdmin(UserAdmin):
    # 「まずユーザー名とパスワードを登録してください」の文言を非表示にする
    add_form_template = None

    fieldsets = (
        (None, {'fields':('email', 'password')}),
        ('Personal info', {'fields':('userid', 'username', 'thumbnail', 'self_intro')}),
        ('Permissions', {'fields':('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields':('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes':('wide',), 'fields':('email', 'password1', 'password2'),}),
    )

    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'username', 'userid', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'userid')
    ordering = ('email',)


admin.site.register(User, MyUserAdmin)
admin.site.register(Message)
admin.site.register(Friend)
admin.site.register(Good)
admin.site.register(Share)
