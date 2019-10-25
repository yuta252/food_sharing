from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail

from ssd.test import inference

class UserManager(BaseUserManager):
    """User Manager"""
    use_in_migration = True

    def _create_user(self, email, password, **extra_fields):
        """メールアドレスの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """is_staff(管理サイトにログイン可否）と、is_superuser(全ての権限）をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """SuperUserは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self._create_user(email, password, **extra_fields)

# User class
class User(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル"""
    class Meta:
        db_table = 'user'

    email = models.EmailField('email_address', unique=True)
    userid = models.CharField('userid', max_length=20, unique=True, help_text='Requied. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
        error_messages={'unique':'A user with that username already exists.'})
    username = models.CharField('username', max_length=30, help_text='Requied. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
    thumbnail = models.ImageField('thumbnail', upload_to='thumbnail', default='./thumnail/noimage.png')
    self_intro = models.CharField('self_intro', max_length=120, null=True, blank=True)

    is_staff = models.BooleanField('staff_status', default=False, help_text='Designates whether the user can log into this admin site')
    is_active = models.BooleanField('active', default=True, help_text='Designates whether this user should be treated as active')
    date_joined = models.DateTimeField('date_joined', default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def email_user(self, subject, message, from_email=None, **kwargs):
        """ユーザーにEmailを送信"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        return self.userid

    def get_short_name(self):
        return self.userid


# Message class
class Message(models.Model):

    class Meta:
        db_table = 'message'
        ordering = ('-pub_date',)

    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='message_owner')
    public = models.BooleanField(default=True)
    content = models.TextField(max_length=150)
    # 画像格納をあとで実装 blankをあとで削除
    post_pic = models.ImageField('post_pic', upload_to='postpic/%Y/%m/%d', blank=True)
    share_id = models.IntegerField(default=-1)
    good_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.content) + '(' + str(self.owner) + ')'

    def get_share(self):
        return Message.objects.get(id=self.share_id)

    def get_inference(self, path):
        result = inference(image_path=str(path))
        return result


# Friends class
class Friend(models.Model):

    class Meta:
        db_table = 'friend'

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_owner')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

# Good class
class Good(models.Model):

    class Meta:
        db_table = 'good'

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='good_owner')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    def __str__(self):
        return 'good for' + str(self.message) + '(by' + str(self.owner) + ')'

# Share class
class Share(models.Model):

    class Meta:
        db_table = 'share'

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='share_owner')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    def __str__(self):
        return 'share for' + str(self.message) + '(by' + str(self.owner) + ')'

# Comment class
class Comment(models.Model):

    class Meta:
        db_table = 'comment'

    owner = models.ForeignKey(User, verbose_name='reply_owner',on_delete=models.CASCADE, related_name='reply_owner')
    reply = models.TextField('reply_content',max_length=150)
    message = models.ForeignKey(Message, verbose_name='message_connected',on_delete=models.CASCADE)
    created_at = models.DateTimeField('reply_date', default=timezone.now)

    def __str__(self):
        return str(self.reply) + '(by' + str(self.owner) + ')'