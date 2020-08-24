import random
import re
import string

from django.utils.text import slugify


def generate_random_string(max_length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(max_length))


def unique_slugify(instance, queryset=None, value=None, max_length=255):
    """function used to give a unique slug to an instance"""

    if not value:
        value = generate_random_string(max_length)

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
