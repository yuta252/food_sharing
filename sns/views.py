import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.core.mail import send_mail
from django.http import Http404, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.db.models import Q
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, DetailView, FormView
from django.views.generic.edit import ModelFormMixin, UpdateView
from logging import StreamHandler, DEBUG, Formatter, FileHandler, getLogger

from .forms import SignupForm, LoginForm, MessageForm, CommentForm, UserEditForm, MyPasswordChangeForm, MyPasswordResetForm, MySetPasswordForm, EmailChangeForm
from .models import User, Message, Friend, Good, Share, Comment

User = get_user_model()

logger = getLogger(__name__)
log_fmt = Formatter('%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s')
handler = StreamHandler()
handler.setLevel('INFO')
handler.setFormatter(log_fmt)
logger.addHandler(handler)
logger.setLevel(DEBUG)

# Sign up auth
class SignupView(CreateView):
    """ユーザー仮登録"""
    form_class = SignupForm
    template_name = 'sns/signup.html'

    def form_valid(self, form):
        """
            仮登録と本登録のメールの発行
            仮登録と本登録の切り替えはis_active
        """
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('sns/mail_template/create/subject.txt', context)
        message = render_to_string('sns/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('sns:signup_done')

class SignupDone(TemplateView):
    """ユーザー仮登録画面"""
    template_name = 'sns/signup_done.html'

class SignupComplete(TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'sns/signup_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)

    def get(self, request, **kwargs):
        """tokenが正しければ本登録"""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()
        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 本登録
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)
        return HttpResponseBadRequest()

# Login page
class Login(LoginView):
    form_class = LoginForm
    template_name = 'sns/login.html'

# Logout page
class Logout(LoginRequiredMixin, LogoutView):
    template_name = 'sns/login.html'

# ユーザーのプロフィール編集
class UserEditView(LoginRequiredMixin, UpdateView):
    template_name = 'sns/user_edit.html'
    model = User
    form_class = UserEditForm
    success_url = reverse_lazy('sns:mypage')

# パスワードの変更
class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('sns:password_change_done')
    template_name = 'sns/password_change.html'

# パスワード変更完了
class PasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'sns/password_change_done.html'

# パスワード変更用URLの送付ページ
class PasswordReset(PasswordResetView):
    subject_template_name = 'sns/mail_template/password_reset/subject.txt'
    email_template_name = 'sns/mail_template/password_reset/message.txt'
    template_name = 'sns/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('sns:password_reset_done')

# パスワード変更用URLを送付完了ページ
class PasswordResetDone(PasswordResetDoneView):
    template_name = 'sns/password_reset_done.html'

# 新パスワード入力ページ
class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    success_url = reverse_lazy('sns:password_reset_complete')
    template_name = 'sns/password_reset_confirm.html'

# 新パスワード設定完了ページ
class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'sns/password_reset_complete.html'

# メールアドレス変更
class EmailChange(LoginRequiredMixin, FormView):
    template_name = 'sns/email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URL送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('sns/mail_template/email_change/subject.txt', context)
        message = render_to_string('sns/mail_template/email_change/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('sns:email_change_done')

# メール送信完了画面
class EmailChangeDone(LoginRequiredMixin, TemplateView):
    template_name = 'sns/email_change_done.html'

# メールのリンク後のアドレス変更
class EmailChangeComplete(LoginRequiredMixin, TemplateView):
    template_name = 'sns/email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)
        except SignatureExpired:
            return HttpResponseBadRequest()

        except BadSignature:
            return HttpResponseBadRequest()

        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)

# Mainpage view
class IndexView(LoginRequiredMixin, ListView, ModelFormMixin):

    model = Message
    form_class = MessageForm
    template_name = 'sns/index.html'

    def get_queryset(self):
        """自分が登録したFriendsを取得"""
        friends = Friend.objects.filter(owner=self.request.user)
        # Friends Querysetでは抽出できないのでFriend roop処理してUser Querysetを取り出す
        friends_list = []
        friends_share_list = []
        for f in friends:
            friend = f.user
            friends_list.append(friend)
            # friendがShareしたMessageを取得
            share_all = friend.share_owner.all()
            for share in share_all:
                friends_share_list.append(share.message.id)
        friends_group = User.objects.filter(email__in=friends_list)

        queryset = Message.objects.filter(Q(owner=self.request.user) | Q(owner__in=friends_group) | Q(id__in=friends_share_list), public=True).order_by('-pub_date')

        # 検索フォームによる検索結果の表示
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(owner__username__icontains=keyword)|Q(content__icontains=keyword)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['good'] = Good.objects.filter(owner=self.request.user)
        context['share'] = Share.objects.filter(owner=self.request.user)
        return context


    # 投稿用の処理
    def get(self, request, *args, **kargs):
        self.object = None
        return super().get(request, *args, **kargs)

    def post(self, request, *args, **kargs):
        self.object = None
        self.object_list = self.get_queryset()
        form = self.get_form()
        logger.info('form:{}'.format(form))
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """is_valid後、セーブする前に必須項目ownerにuserの値を紐つける処理"""
        owner = self.request.user
        public = self.request.POST.get('public')
        obj = form.save(commit=False)
        obj.owner = owner
        obj.public = public
        obj.save()
        """Deep learningの推定処理"""
        message = Message.objects.filter(id=obj.id)[0]
        logger.info('message: {}'.format(message))
        result = message.get_inference(path=message.post_pic)
        logger.info('result: {}'.format(result))

        return redirect('sns:index')

# Private
class PrivateView(LoginRequiredMixin, ListView):

    model = Message
    template_name = 'sns/private.html'

    def get_queryset(self):
        """自分の投稿かつプライベート項目のみ表示"""
        queryset = Message.objects.filter(owner=self.request.user, public=False).order_by('-pub_date')
        """検索フォームによる検索結果の表示"""
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(owner__username__icontains=keyword)|Q(content__icontains=keyword)
            )
        return queryset


# ALL Post
class GlobalView(LoginRequiredMixin, ListView):

    model = Message
    template_name = 'sns/global.html'

    def get_queryset(self):
        """公開されている全ての投稿を表示"""
        queryset = Message.objects.filter(public=True).order_by('-pub_date')
        """検索フォームによる検索結果の表示"""
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(owner__username__icontains=keyword)|Q(content__icontains=keyword)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['good'] = Good.objects.filter(owner=self.request.user)
        context['share'] = Share.objects.filter(owner=self.request.user)
        return context


# Mypage
class MypageView(LoginRequiredMixin, ListView):

    model = Message
    template_name = 'sns/mypage.html'

    def get_queryset(self):
        """検索フォームによる検索結果の表示"""
        queryset = Message.objects.filter(owner=self.request.user).order_by('-pub_date')
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(owner__username__icontains=keyword)|Q(content__icontains=keyword)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['good'] = Good.objects.filter(owner=self.request.user)
        context['share'] = Share.objects.filter(owner=self.request.user)
        return context

# Setting
class SettingView(LoginRequiredMixin, UpdateView):
    template_name = 'sns/setting.html'
    model = User
    form_class = UserEditForm
    success_url = reverse_lazy('sns:mypage')


# Friends page
class FriendsView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'sns/otheruser.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        f_id = self.kwargs['pk']
        friend = User.objects.filter(id=f_id)[0]

        user = self.request.user
        success = not(Friend.objects.filter(owner=user, user=friend).exists())
        # pkでFriendsのユーザーを取得
        context['friend'] = User.objects.filter(id=f_id)[0]

        if success:
            context['follow'] = 'フォロー'
            context['followclass'] = 'follow-btn'
        else:
            context['follow'] = 'フォロー解除'
            context['followclass'] = 'nofollow-btn'

        context['good'] = Good.objects.filter(owner=user)
        context['share'] = Share.objects.filter(owner=user)

        return context

    def get_queryset(self):
        queryset = Message.objects.filter(owner__id=self.kwargs['pk']).order_by('-pub_date')
        return queryset

# Follow friend AJAX
class FollowFriendView(View):
    """既にフレンド登録しているかチェック"""
    def get(self, request, *args, **kwargs):
        f_id = request.GET.get('friend')
        friend = User.objects.filter(id=f_id)[0]

        user = self.request.user
        success = not(Friend.objects.filter(owner=user, user=friend).exists())

        if success:
            obj = Friend.objects.create(owner=user, user=friend)
            display = 'フォロー解除'
            addcss = 'nofollow-btn'
            removecss = 'follow-btn'
        else:
            obj = Friend.objects.get(owner=user, user=friend)
            obj.delete()
            display = 'フォロー'
            addcss = 'follow-btn'
            removecss = 'nofollow-btn'
        data = {
            'success': success,
            'display': display,
            'addcss': addcss,
            'removecss': removecss,
        }
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')

# Good Message AJAX
class GoodMessageView(View):
    """既にメッセージにいいねしているかチェック"""
    def get(self, request, *args, **kwargs):
        m_id = request.GET.get('message')
        message = Message.objects.filter(id=m_id)[0]

        user = self.request.user
        success = not(Good.objects.filter(owner=user, message=message).exists())

        if success:
            obj = Good.objects.create(owner=user, message=message)
            display = 'いいね解除'
            addcss = 'nogood-btn'
            removecss = 'good-btn'
        else:
            obj = Good.objects.get(owner=user, message=message)
            obj.delete()
            display = 'いいね'
            addcss = 'good-btn'
            removecss = 'nogood-btn'

        data = {
            'success': success,
            'display': display,
            'addcss': addcss,
            'removecss': removecss,
        }
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')

# Share Message AJAX
class ShareMessageView(View):
    """既にメッセージにいいねしているかチェック"""
    def get(self, request, *args, **kwargs):
        m_id = request.GET.get('message')
        message = Message.objects.filter(id=m_id)[0]

        user = self.request.user
        success = not(Share.objects.filter(owner=user, message=message).exists())

        if success:
            obj = Share.objects.create(owner=user, message=message)
            display = 'シェア解除'
            addcss = 'noshare-btn'
            removecss = 'share-btn'
        else:
            obj = Share.objects.get(owner=user, message=message)
            obj.delete()
            display = 'シェア'
            addcss = 'share-btn'
            removecss = 'noshare-btn'

        data = {
            'success': success,
            'display': display,
            'addcss': addcss,
            'removecss': removecss,
        }
        data = json.dumps(data)
        return HttpResponse(data, content_type='application/json')


# Message detail
class MessageDetailView(LoginRequiredMixin, DetailView, ModelFormMixin):
    model = Message
    form_class = CommentForm
    template_name = 'sns/message.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pkでメッセージメソッドを絞る
        context['message'] = Message.objects.filter(id=self.kwargs['pk'])[0]
        context['reply'] = Comment.objects.filter(message=self.kwargs['pk'])
        context['good'] = Good.objects.filter(owner=self.request.user)
        context['share'] = Share.objects.filter(owner=self.request.user)
        return context

    def get_queryset(self):
        """検索フォームによる検索結果の表示"""
        queryset = Message.objects.order_by('-pub_date')
        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(owner__username__icontains=keyword)|Q(content__icontains=keyword)
            )
        return queryset

    # リプライの処理
    def get(self, request, *args, **kargs):
        self.object = None
        return super().get(request, *args, **kargs)

    def post(self, request, *args, **kargs):
        self.object = None
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """is_valid後、セーブする前に必須項目ownerにuser、messageの値を紐つける処理"""
        owner = self.request.user
        obj = form.save(commit=False)
        obj.owner = owner
        message_id = self.kwargs['pk']
        message = Message.objects.get(id=message_id)
        obj.message = message
        obj.save()
        return redirect('sns:message', pk=message_id)