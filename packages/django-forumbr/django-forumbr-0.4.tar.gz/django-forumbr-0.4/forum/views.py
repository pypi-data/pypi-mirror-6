#-*- coding:utf-8 -*-

from functools import wraps
import json

from django.core.urlresolvers import reverse
from django.db import transaction
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404 as get_object
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import available_attrs
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView

from app_settings import *
from .constants import MARKUP_EDITORS
from models import MessageBox, Message
from models import Category
from models import Forum
from models import Profile
from forms import ReplyForm, ThreadForm
from forms import ProfileForm, RateForm
from forms import MessageForm
from urlparse import urlparse, urljoin


def is_path(target):
    parsed = urlparse(target)
    return parsed.netloc == '' and parsed.scheme == ''


def is_internal_url(request, target):
    ref_url = urlparse(request.get_host())
    test_url = urlparse(urljoin(request.get_host(), target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def user_passes_test(test_func, redirect_field_name):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            return redirect(reverse('forum:register_profile') +
                            '?next=' + request.get_full_path())

        return _wrapped_view

    return decorator


def profile_required(function=None, redirect_field_name='next'):
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'forum_profile'),
        redirect_field_name
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


class ProtectedMixin(object):
    _profile = None

    @method_decorator(login_required)
    @method_decorator(profile_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedMixin, self).dispatch(*args, **kwargs)

    @property
    def profile(self):
        return self.request.user.forum_profile


class IndexView(TemplateView):
    template_name = 'forum/index.html'

    def get(self, request):
        return self.render_to_response({
            'category_set': Category.objects.active()
        })


class PublicProfileView(TemplateView):
    template_name = 'forum/profile.html'

    def get(self, request, nickname):
        return self.render_to_response({
            'is_self': False,
            'profile': get_object(Profile, nickname=nickname)
        })


class ProfileView(ProtectedMixin, TemplateView):
    template_name = 'forum/profile.html'

    def get(self, request):
        return self.render_to_response({
            'is_self': True,
            'profile': request.user.forum_profile
        })


class EditProfileView(ProtectedMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'forum/edit_profile.html'

    def form_valid(self, form):
        messages.info(self.request, _('Profile updated'))
        return super(EditProfileView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.kwargs.get('next') or 'forum:profile')

    def get_object(self, queryset=None):
        return self.profile

    def get_context_data(self, **kwargs):
        context_data = super(EditProfileView, self).get_context_data(**kwargs)
        context_data['profile'] = self.profile
        return context_data


class SendMessageView(ProtectedMixin, CreateView):
    _recipient = None
    model = Message
    form_class = MessageForm
    template_name = 'forum/send_message.html'

    @property
    def recipient(self):
        nickname = self.kwargs['nickname']
        self._recipient = self._recipient \
            or get_object(Profile, nickname=nickname)
        return self._recipient

    def form_valid(self, form):
        form.save(self.profile, self.recipient)
        messages.success(self.request, _('Message sent.'))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('forum:messages')

    def get_context_data(self, **kwargs):
        context = super(SendMessageView, self).get_context_data(**kwargs)
        context['profile'] = self.profile
        context['recipient'] = self.recipient
        return context


class UserMessageView(ProtectedMixin, DetailView):
    pk_url_kwarg = 'pk_message'
    template_name = 'forum/message.html'
    context_object_name = 'pvt'

    def get_queryset(self):
        profile = self.request.user.forum_profile
        return profile.messages.active()

    def get_context_data(self, **kwargs):
        context = super(UserMessageView, self).get_context_data(**kwargs)
        context['profile'] = self.profile
        return context

    def get(self, request, *args, **kwargs):
        self.get_object().read(commit=True)
        return super(UserMessageView, self).get(request, *args, **kwargs)


class UserMessagesView(ProtectedMixin, ListView):
    template_name = 'forum/messages.html'
    paginate_by = PAGINATE_MESSAGES_BY

    def get_queryset(self):
        profile = self.request.user.forum_profile
        return profile.messages.active()

    def get_context_data(self, **kwargs):
        context = super(UserMessagesView, self).get_context_data(**kwargs)
        context['profile'] = self.request.user.forum_profile
        context['new_messages'] = self.get_queryset().filter(was_read=False)
        return context


class CategoryView(TemplateView):
    template_name = 'forum/index.html'

    def get(self, request, *args, **kwargs):
        category_set = Category.objects.active().filter(pk=self.kwargs['pk_category'])
        return self.render_to_response({
            'category_set': category_set
        })


class ForumView(TemplateView):
    template_name = 'forum/forum.html'

    def get_context_data(self, **kwargs):
        pk_forum = self.kwargs['pk_forum']
        forum = get_object(Forum.objects.active(), pk=pk_forum)
        category = forum.category
        threads = forum.threads.active()
        page_number = self.kwargs.get('page', 1)
        object_list = Paginator(threads, PAGINATE_THREADS_BY).page(page_number)
        context = super(ForumView, self).get_context_data(**kwargs)
        context['category'] = category
        context['forum'] = forum
        context['object_list'] = object_list
        return context


class ThreadView(TemplateView):
    template_name = 'forum/thread.html'


def thread_view(request, pk_forum, pk_thread):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    category = forum.category
    threads = forum.threads.active()
    thread = get_object(threads, pk=pk_thread)
    replies = thread.replies.active()
    page_number = request.GET.get('page', 1)
    object_list = Paginator(replies, PAGINATE_REPLIES_BY).page(page_number)
    form = None

    # FIXME - form reference problem
    if ALLOW_INLINE_REPLY:
        form = ReplyForm(request.POST or None)

        if form.is_bound and form.is_valid():
            new_reply = form.save()
            return redirect(new_reply)

    thread.update_views(request)
    return render(request, 'forum/thread.html', {
        'category': category,
        'form': form,
        'forum': forum,
        'thread': thread,
        'object_list': object_list
    })


@login_required
@profile_required
@transaction.atomic
def new_thread_view(request, pk_forum, pk_thread=None):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    category = forum.category

    thread_form = ThreadForm(
        request.POST or None,
        request.method == 'POST' and request.FILES or None)
    reply_form = ReplyForm(
        request.POST or None,
        request.method == 'POST' and request.FILES or None)
    profile = request.user.forum_profile

    if thread_form.is_bound and reply_form.is_bound \
            and thread_form.is_valid() and reply_form.is_valid():
        new_thread = thread_form.save(profile, forum)
        reply_form.save(profile, forum, new_thread)
        return redirect(new_thread)
    return render(request, 'forum/new_thread.html', {
        'category': category,
        'forum': forum,
        'thread_form': thread_form,
        'reply_form': reply_form
    })


@login_required
@profile_required
@transaction.atomic
def reply_view(request, pk_forum, pk_thread):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    category = forum.category
    threads = forum.threads.active()
    thread = get_object(threads, pk=pk_thread)
    form = ReplyForm(request.POST or None)
    editor_name = MARKUP_EDITORS[MARKUP]
    editor_style = 'js/forum/markitup/sets/%s/style.css' % editor_name
    editor_set = 'js/forum/markitup/sets/%s/set.js' % editor_name

    if form.is_bound and form.is_valid():
        new_reply = form.save(request.user.forum_profile, forum, thread)
        return redirect(new_reply)

    return render(request, 'forum/reply.html', {
        'category': category,
        'forum': forum,
        'thread': thread,
        'form': form,
        'editor_name': editor_name,
        'editor_style': editor_style,
        'editor_set': editor_set,
    })


@login_required
@profile_required
def rate_reply_view(request, pk_forum, pk_thread, pk_reply):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    threads = forum.threads.active()
    thread = get_object(threads, pk=pk_thread)
    reply = get_object(thread.replies.active(), pk=pk_reply)

    form = RateForm(request.POST or None)
    if form.is_bound and form.is_valid():
        rating = form.save(request.profile, reply)
        return HttpResponse(
            json.dumps({'status': 'ok', 'message': 'success'}),
            mimetype='application/json')

    return HttpResponse(
        json.dumps({'status': 'error', 'message': 'invalid form data'}),
        mimetype='application/json')


@login_required
def register_profile_view(request):
    next = request.REQUEST.get('next', None)

    if request.method == 'POST':
        profile, created = Profile.objects.get_or_create(user=request.user)
        box = MessageBox.objects.get_or_create(profile=profile)
        messages.info(request, _("You now have a forum profile! Please, enjoy ; )"))

        if next is not None and is_path(next):
            return redirect(next)

        return redirect('forum:index')

    return render(request, 'forum/register_profile.html',
                  {'next': next})