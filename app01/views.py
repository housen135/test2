import os
from bbs import settings
from PIL import Image, ImageDraw, ImageFont
import bs4
from bs4 import BeautifulSoup
import json
from django.db.models import Count
from utils.mypage import Pagination
from io import BytesIO, StringIO
from django.db import transaction
from django.db.models import F
from django.db.models.functions import TruncMonth
import random
from django.shortcuts import render, redirect, reverse, HttpResponse

from app01 import myforms
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from html.parser import HTMLParser


def register(request):
    form_obj = myforms.MyRegForm()
    if request.method == 'POST':
        back_dic = {'code': 200, 'msg': ''}
        form_obj = myforms.MyRegForm(request.POST)
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            print(file_obj)
            if file_obj:
                clean_data['avatar'] = file_obj
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 400
            back_dic['msg'] = form_obj.errors  # 校验数据
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        print('post ok')
        back_dic = {'infcode': 200, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        if code.upper() == request.session.get('code').upper():
            user_obj = auth.authenticate(username=username, password=password)
            if user_obj:
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['infcode'] = 400
                back_dic['msg'] = '用户名或者密码错误'
        else:
            back_dic['infcode'] = 410
            back_dic['msg'] = '验证码错'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


def get_random_ground():
    return random.randint(140, 255), random.randint(140, 255), random.randint(150, 250)


def get_random():
    return random.randint(0, 170), random.randint(0, 170), random.randint(0, 170)


def font_choice():
    return random.choice(['111.ttf', '222.ttf'])


fontchoice = font_choice()


def get_code(request):
    img_obj = Image.new('RGB', (300, 35), get_random_ground())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('static/font/{}'.format(fontchoice), 30)
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_num = str(random.randint(0, 9))
        temp = random.choice([random_upper, random_lower, random_num])
        img_draw.text((i*45+45, 0), temp, get_random(), img_font)
        code += temp
    print(code)

    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    article_list = models.Article.objects.all()
    current_page = request.GET.get('page', 1)
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'home.html', locals())


@login_required
def logout(request):
    auth.logout(request)  # request.session.flush()
    return redirect(reverse('login'))


@login_required
def set_password(request):
    if request.is_ajax():
        print('ok')
        back_dic = {'code': 200, 'msg': ''}
        if request.method == 'POST':
            print('set_pwd post ok')
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                is_right = request.user.check_password(old_password)
                if is_right:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['url'] = '/login/'
                else:
                    back_dic['code'] = 400
                    back_dic['msg'] = '老密码不对'
            else:
                back_dic['code'] = 400
                back_dic['msg'] = '两次输入密码不一致'
            return JsonResponse(back_dic)
    print('error ajax')


def site(request, username, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'errors.html')
    blog_obj = user_obj.blog
    article_queryset = models.Article.objects.filter(blog=blog_obj)

    # print(article_queryset.values('title'))
    # cat_list = models.Category.objects.filter(article__pk__in=article_queryset.values('pk')).annotate(cat_num=Count(models.Category)).values_list('name','cat_num','pk')
    # print(cat_list)
    if kwargs:

        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':

            article_queryset = article_queryset.filter(category_id=param)
        if condition == 'tag':
            article_queryset = article_queryset.filter(tags__id=param)
        if condition == 'date':
            year, month = param.split('-')
            article_queryset = article_queryset.filter(
                create_time__year=year, create_time__month=month)

    # cat_list =models.Category.objects.filter(blog=blog_obj).annotate(cat_num=Count('article__pk')).values_list('name','cat_num','pk')
    # print(cat_list)
    # tag_list =models.Tag.objects.filter(blog=blog_obj).annotate(tag_num=Count('article__pk')).values_list('name','tag_num','pk')

    # date_list =models.Article.objects.filter(blog=blog_obj).annotate(month = TruncMonth('create_time')).values('month').annotate(date_num=Count('pk')).values_list('month','date_num')
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    article = models.Article.objects.filter(pk=article_id).first()
    comments = models.Comment.objects.filter(article=article).all()
    print(comments)
    # user_obj = models.UserInfo.objects.filter(username=username).first()
    # blog_obj = user_obj.blog
    # print(blog_obj)
    # article_list = models.Article.objects.filter(blog=blog_obj,title=title)
    return render(request, 'article_detail.html', locals())


def get_UpAndDown(request):
    if request.is_ajax():
        back_dic = {'code': 200, 'msg': ''}
        print('ajax ok')
        if request.method == 'POST':
            article_id = request.POST.get('article_id')
            user_obj = request.user
            if user_obj:
                is_up = request.POST.get('is_up')
                is_up = json.loads(is_up)
                article_obj = models.Article.objects.filter(
                    pk=article_id).first()
                print('first之后', article_obj)
                print('queryset', models.Article.objects.filter(pk=article_id))
                # print(article_obj.blog.article_set.all())
                if not article_obj.blog.userinfo == request.user:
                    is_done = models.UpAndDown.objects.filter(
                        user=request.user, article=article_obj).first()
                    if not is_done:
                        if is_up:
                            models.Article.objects.filter(
                                pk=article_id).update(up_num=F('up_num')+1)
                            back_dic['msg'] = '点赞成功'
                        else:
                            models.Article.objects.filter(
                                pk=article_id).update(down_num=F('up_num')+1)
                            back_dic['msg'] = '点踩成功'
                        models.UpAndDown.objects.create(
                            user=request.user, article=article_obj, is_up=is_up)
                    else:
                        back_dic['code'] = 400
                        back_dic['msg'] = '已经点过'
                else:
                    back_dic['code'] = 400
                    back_dic['msg'] = '自己不能点'
            else:
                back_dic['code'] = 400
                back_dic['msg'] = '<p><a href="/login/">请登录</p>'
            return JsonResponse(back_dic)
        return JsonResponse(back_dic)


def comment(request):
    print('comment ok')
    if request.is_ajax():
        back_dic = {'code': 200, 'msg': ''}
        if request.method == 'POST':
            user_obj = request.user
            article_id = request.POST.get('article_id')
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')
            article = models.Article.objects.filter(pk=article_id).first()
            print('comment', article)
            with transaction.atomic():
                models.Comment.objects.create(
                    content=content, user=user_obj, article=article, parent_id=parent_id)
                models.Article.objects.filter(pk=article_id).update(
                    comment_num=F('comment_num')+1)
            back_dic['msg'] = '评论成功'
        else:
            back_dic['code'] = 400
            back_dic['msg'] = '失败'
        return JsonResponse(back_dic)


@login_required
def back_set(request):
    user_blog = request.user.blog
    article_objs = models.Article.objects.filter(blog=user_blog)

    return render(request, 'back/back_article.html', locals())


@login_required
def back_add(request):

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        blog = request.user.blog
        category_id = request.POST.get('cat')
        tags = request.POST.getlist('tags')

        soup = BeautifulSoup(content, 'html5lib')
        bs_tags = soup.find_all()
        for bs_tag in bs_tags:
            if bs_tag.name == 'script':
                bs_tag.decompose()
        text = soup.get_text()
        print(text)
        desc = text[0:150]
        print(desc)
        soup = HTMLParser().unescape(soup)
        soup = str(soup).replace('&lt;', '<').replace(
            '&gt;', '>').replace('&nbsp;', ' ')
        add_article = models.Article.objects.create(
            title=title, content=str(soup), desc=desc, blog=blog, category_id=category_id)
        tag_add_list = []
        for i in tags:
            tag_add_list.append(models.Article2Tag(
                article=add_article, tag_id=i))
        models.Article2Tag.objects.bulk_create(tag_add_list)
        return redirect('/back_set/')

    user_blog = request.user.blog
    tag_list = models.Tag.objects.filter(blog=user_blog)
    cat_list = models.Category.objects.filter(blog=user_blog)
    print(cat_list)
    return render(request, 'back/back_add.html', locals())


def upload_img(request):
    if request.method == 'POST':
        back_dic = {'error': 0, 'message': ''}
        file_obj = request.FILES.get('imgFile')
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url']='/media/article_img/%s'%file_obj.name
        return JsonResponse(back_dic)

@login_required
def set_img(request):
    username = request.user.username
    if request.method =='POST':
        img = request.FILES.get('avatar')
        print('img',img.name, type(img))
        user_obj=models.UserInfo.objects.filter(pk=request.user.pk).update(avatar='avatar/'+img.name)
        # user_obj =request.user
        # user_obj.avatar = img
        user_obj.save()
    return render(request,'set_img.html',locals())


            # Create your views here
