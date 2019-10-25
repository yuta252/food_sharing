from django.urls import path
from . import views

app_name = 'sns'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/done', views.SignupDone.as_view(), name='signup_done'),
    path('signup/complete/<token>/', views.SignupComplete.as_view(), name='signup_complete'),
    path('user/edit_profile/<int:pk>/', views.UserEditView.as_view(), name='edit_profile'),
    path('email/change/', views.EmailChange.as_view(), name='email_change'),
    path('email/change/done/', views.EmailChangeDone.as_view(), name='email_change_done'),
    path('email/change/complete/<str:token>/', views.EmailChangeComplete.as_view(), name='email_change_complete'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Login.as_view(), name='logout'),
    path('', views.IndexView.as_view(), name='index'),
    path('private/', views.PrivateView.as_view(), name='private'),
    path('global/', views.GlobalView.as_view(), name='global'),
    path('mypage/', views.MypageView.as_view(), name='mypage'),
    path('setting/<int:pk>/', views.SettingView.as_view(), name='setting'),
    path('friends/<int:pk>/', views.FriendsView.as_view(), name='friends'),
    path('message/<int:pk>/', views.MessageDetailView.as_view(), name='message'),
    path('follow_ajax/', views.FollowFriendView.as_view(), name='follow_ajax'),
    path('good_ajax/', views.GoodMessageView.as_view(), name='good_ajax'),
    path('share_ajax/', views.ShareMessageView.as_view(), name='share_ajax'),
]