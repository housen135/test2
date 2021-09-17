from django.template import Library
from app01 import models
from django.db.models.functions import TruncMonth
from django.db.models import Count
register = Library()

@register.inclusion_tag('left_menu.html')

def index(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog_obj =user_obj.blog

    cat_list =models.Category.objects.filter(blog=blog_obj).annotate(cat_num=Count('article__pk')).values_list('name','cat_num','pk')
    print(cat_list)
    tag_list =models.Tag.objects.filter(blog=blog_obj).annotate(tag_num=Count('article__pk')).values_list('name','tag_num','pk')

    date_list =models.Article.objects.filter(blog=blog_obj).annotate(month = TruncMonth('create_time')).values('month').annotate(date_num=Count('pk')).values_list('month','date_num')
    return locals()