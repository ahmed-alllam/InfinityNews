import random
import re
import string

from django.contrib.auth import get_user_model
from django.utils.text import slugify


def generate_random_string():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


def generate_random_username():
    username = generate_random_string()
    while get_user_model().objects.filter(username=username):
        username = generate_random_string()

    return username


def unique_slugify(instance, queryset=None, value=generate_random_string(), max_length=255):
    """function used to give a unique slug to an instance"""

    slug = slugify(value, allow_unicode=True)
    slug = slug[:max_length]  # limit its len to max_length of slug field

    def _slug_strip(_value):
        """removes the '-' separator from the end or start of the string"""
        return re.sub(r'^%s+|%s+$' % ('-', '-'), '', _value)

    slug = _slug_strip(slug)
    original_slug = slug

    if not queryset:
        queryset = instance.__class__.objects.all()

    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    _next = 2
    while not slug or queryset.filter(slug=slug):
        slug = original_slug
        end = '-%s' % _next
        if len(slug) + len(end) > max_length:
            slug = slug[:max_length - len(end)]
            slug = _slug_strip(slug)
        slug = '%s%s' % (slug, end)
        _next += 1

    return slug
