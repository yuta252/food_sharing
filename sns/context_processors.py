from .models import Good, Share, Message, Friend

def common(request):
    """テンプレートに毎回渡すデータ"""
    user = request.user
    # good_count = Good.objects.filter(message__owner=user).count()
    # share_count = Share.objects.filter(message__owner=user).count()
    # report_count = Message.objects.filter(owner=user).count()
    # support_count = Friend.objects.filter(owner=user).count()
    # supporter_count = Friend.objects.filter(user__email=user).count()
    good_count = 1
    share_count = 1
    report_count = 1
    support_count = 1
    supporter_count = 1
    context = {
        'user': user,
        'good_count': good_count,
        'share_count': share_count,
        'report_count': report_count,
        'support_count': support_count,
        'supporter_count': supporter_count,
    }
    return context