# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from odnoklassniki_api.models import OdnoklassnikiManager, OdnoklassnikiPKModel, OdnoklassnikiModel
from odnoklassniki_api.fields import JSONField
from odnoklassniki_groups.models import Group
from odnoklassniki_users.models import User
from odnoklassniki_api.decorators import fetch_all, atomic
import logging
import re

log = logging.getLogger('odnoklassniki_discussions')

DISCUSSION_TYPES = [
    'GROUP_TOPIC',
    'GROUP_PHOTO',
    'USER_STATUS',
    'USER_PHOTO',
    'USER_FORUM',
    'USER_ALBUM',
    'USER_2LVL_FORUM',
    'MOVIE',
    'SCHOOL_FORUM',
    'HAPPENING_TOPIC',
    'GROUP_MOVIE',
    'CITY_NEWS',
    'CHAT',
]
COMMENT_TYPES = ['ACTIVE_MESSAGE']

DISCUSSION_TYPE_CHOICES = [(type, type) for type in DISCUSSION_TYPES]
COMMENT_TYPE_CHOICES = [(type, type) for type in COMMENT_TYPES]

class DiscussionRemoteManager(OdnoklassnikiManager):

    def fetch(self, **kwargs):
        if 'id' in kwargs and 'type' in kwargs:
            return self.fetch_one(**kwargs)
        elif 'group' in kwargs:
            return self.fetch_for_group(**kwargs)
        else:
            raise Exception("Wrong atributes for Discussion.remote.fetch() method kwargs=%" % kwargs)

    @atomic
    def fetch_one(self, id, type, **kwargs):
        if type not in DISCUSSION_TYPES:
            raise ValueError("Wrong value of type argument %s" % type)

        kwargs['discussionId'] = id
        kwargs['discussionType'] = type
        # with `fields` response doesn't contain `entities` field
        #kwargs['fields'] = self.get_request_fields('discussion')
        return super(DiscussionRemoteManager, self).fetch(method='get_one', **kwargs)

    def update_discussions_count(self, instances, group, *args, **kwargs):
        group.discussions_count = len(instances)
        group.save()
        return instances

    @atomic
    @fetch_all(return_all=update_discussions_count)
    def fetch_for_group(self, group, count=100, **kwargs):
        kwargs['gid'] = group.pk
        kwargs['count'] = int(count)
        kwargs['patterns'] = 'POST'
        kwargs['fields'] = self.get_request_fields('feed', 'media_topic', prefix=True)

        response = super(DiscussionRemoteManager, self).api_call(method='stream', **kwargs)
        # has_more not in dict and we need to handle pagination manualy
        if 'feeds' not in response:
            del response['anchor']
            return self.model.objects.none(), response

        feed = [feed for feed in response['feeds'] if feed['pattern'] == 'POST']
        discussions = self.parse_response(feed, {'owner_id': group.pk, 'owner_content_type_id': ContentType.objects.get_for_model(group).pk})
        discussions = self.get_or_create_from_list(discussions)

        return discussions, response


class CommentRemoteManager(OdnoklassnikiManager):

    def update_comments_count(self, instances, discussion, *args, **kwargs):
        discussion.comments_count = instances.count()
        discussion.save()
        return instances

    @atomic
    @fetch_all(return_all=update_comments_count)
    def fetch(self, discussion, count=100, **kwargs):
        kwargs['discussionId'] = discussion.pk
        kwargs['discussionType'] = discussion.type
        kwargs['count'] = int(count)

        response = super(CommentRemoteManager, self).api_call(**kwargs)
        comments = self.parse_response(response['comments'], {'discussion_id': discussion.pk})
        comments = self.get_or_create_from_list(comments)

        return comments, response


class Discussion(OdnoklassnikiPKModel):
    class Meta:
        verbose_name = _('Odnoklassniki discussion')
        verbose_name_plural = _('Odnoklassniki discussions')

    methods_namespace = ''
    remote_pk_field = 'object_id'

    owner_content_type = models.ForeignKey(ContentType, related_name='odnoklassniki_discussions_owners')
    owner_id = models.BigIntegerField(db_index=True)
    owner = generic.GenericForeignKey('owner_content_type', 'owner_id')

    author_content_type = models.ForeignKey(ContentType, related_name='odnoklassniki_discussions_authors')
    author_id = models.BigIntegerField(db_index=True)
    author = generic.GenericForeignKey('author_content_type', 'author_id')

    type = models.CharField(max_length=20, choices=DISCUSSION_TYPE_CHOICES)
    title = models.TextField()
    message = models.TextField()

    date = models.DateTimeField()
    last_activity_date = models.DateTimeField(null=True)
    last_user_access_date = models.DateTimeField(null=True)

    new_comments_count = models.PositiveSmallIntegerField(default=0)
    comments_count = models.PositiveSmallIntegerField(default=0)
    likes_count = models.PositiveSmallIntegerField(default=0)

    liked_it = models.BooleanField()

    entities = JSONField(null=True)
    ref_objects = JSONField(null=True)
    attrs = JSONField(null=True)

    remote = DiscussionRemoteManager(methods={
        'get': 'discussions.getList',
        'get_one': 'discussions.get',
        'stream': 'stream.get',
    })

#     def __unicode__(self):
#         return self.name

#     @property
#     def refresh_kwargs(self):
#         return {'ids': [self.pk]}

    @property
    def slug(self):
        return '%s/topic/%s' % (self.owner.slug, self.id)

    def parse(self, response):
        if 'discussion' in response:
            response.update(response.pop('discussion'))

        # in API owner is author
        if 'owner_uid' in response:
             response['author_id'] = response.pop('owner_uid')

        # some name cleaning
        if 'object_type' in response:
            response['type'] = response.pop('object_type')

        if 'like_count' in response:
            response['likes_count'] = response.pop('like_count')

        if 'total_comments_count' in response:
            response['comments_count'] = response.pop('total_comments_count')

        if 'creation_date' in response:
            response['date'] = response.pop('creation_date')

        # response of stream.get has another format
        if '{media_topic' in response['message']:
            regexp = r'{media_topic:?(\d+)?}'
            m = re.findall(regexp, response['message'])
            if len(m):
                response['id'] = m[0]
                response['message'] = re.sub(regexp, '', response['message'])

        return super(Discussion, self).parse(response)

    def save(self, *args, **kwargs):

        # make 2 dicts {id: instance} for group and users from entities
        if self.entities:
            entities = {
                'users': [],
                'groups': [],
            }
            for resource in self.entities.get('users', []):
                entities['users'] += [User.remote.get_or_create_from_resource(resource)]
            for resource in self.entities.get('groups', []):
                entities['groups'] += [Group.remote.get_or_create_from_resource(resource)]
            for field in ['users','groups']:
                entities[field] = dict([(instance.id, instance) for instance in entities[field]])

            # set owner
            for resource in self.ref_objects:
                id = int(resource['id'])
                if resource['type'] == 'GROUP':
                    self.owner = entities['groups'][id]
                elif resource['type'] == 'USER':
                    self.owner = entities['user'][id]
                else:
                    log.warning("Strange type of object in ref_objects %s for duscussion ID=%s" % (resource, self.id))

            # set author
            if self.author_id:
                if self.author_id in entities['groups']:
                    self.author = entities['groups'][self.author_id]
                elif self.author_id in entities['users']:
                    self.author = entities['users'][self.author_id]
                else:
                    log.warning("Imposible to find author with ID=%s in entities of duscussion ID=%s" % (self.author_id, self.id))
                    self.author_id = None

        if self.owner and not self.author_id:
            # of no author_id (owner_uid), so it's equal to owner from ref_objects
            self.author = self.owner

        return super(Discussion, self).save(*args, **kwargs)

    def fetch_comments(self, **kwargs):
        return Comment.remote.fetch(discussion=self, **kwargs)


class Comment(OdnoklassnikiModel):
    class Meta:
        verbose_name = _('Odnoklassniki comment')
        verbose_name_plural = _('Odnoklassniki comments')

    methods_namespace = 'discussions'

    id = models.CharField(max_length=68, primary_key=True)

    discussion = models.ForeignKey(Discussion, related_name='comments')

    author_content_type = models.ForeignKey(ContentType, related_name='odnoklassniki_comments_authors')
    author_id = models.BigIntegerField(db_index=True)
    author = generic.GenericForeignKey('author_content_type', 'author_id')

    reply_to_comment = models.ForeignKey('self', null=True, verbose_name=u'Это ответ на комментарий')

    reply_to_author_content_type = models.ForeignKey(ContentType, null=True, related_name='odnoklassniki_comments_reply_to_authors')
    reply_to_author_id = models.BigIntegerField(db_index=True, null=True)
    reply_to_author = generic.GenericForeignKey('reply_to_author_content_type', 'reply_to_author_id')

    type = models.CharField(max_length=20, choices=COMMENT_TYPE_CHOICES)
    text = models.TextField()

    date = models.DateTimeField()

    likes_count = models.PositiveSmallIntegerField(default=0)
    liked_it = models.BooleanField()

    attrs = JSONField(null=True)

    remote = CommentRemoteManager(methods={
        'get': 'getComments',
        'get_one': 'getComment',
    })

    def parse(self, response):
        if 'like_count' in response:
            response['likes_count'] = response.pop('like_count')
        if 'reply_to_id' in response:
            response['reply_to_author_id'] = response.pop('reply_to_id')
        if 'reply_to_comment_id' in response:
            response['reply_to_comment'] = response.pop('reply_to_comment_id')

        return super(Comment, self).parse(response)

    def save(self, *args, **kwargs):
        if self.author_id:
            try:
                self.author = User.objects.get(pk=self.author_id)
            except User.DoesNotExist:
                self.author = User.remote.fetch(ids=[self.author_id])[0]

        # it's hard to get proper reply_to_author_content_type in case we fetch comments from last
        if self.reply_to_author_id and not self.reply_to_author_content_type:
             self.reply_to_author_content_type = ContentType.objects.get_for_model(User)
#         if self.reply_to_comment_id and self.reply_to_author_id and not self.reply_to_author_content_type:
#             try:
#                 self.reply_to_author = User.objects.get(pk=self.reply_to_author_id)
#             except User.DoesNotExist:
#                 self.reply_to_author = self.reply_to_comment.author

        return super(Comment, self).save(*args, **kwargs)
