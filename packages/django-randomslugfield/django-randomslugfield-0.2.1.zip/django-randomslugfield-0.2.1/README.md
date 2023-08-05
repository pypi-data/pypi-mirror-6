#django-randomslugfield

[![Build Status](https://travis-ci.org/melinko/django-randomslugfield.png?branch=master)](https://travis-ci.org/melinko/django-randomslugfield)
[![Latest PyPI Version](https://pypip.in/v/django-randomslugfield/badge.png)](https://crate.io/packages/django-randomslugfield/)
[![Number of PyPI downloads](https://pypip.in/d/django-randomslugfield/badge.png)](https://crate.io/packages/django-randomslugfield/)

Django field that automatically generates random slugs.

e.g. example.com/kEwD58P

##Getting it

You can get randomslugfield by using `pip` or `easy_install`:

```
$ pip install django-randomslugfield
or
$ easy_install django-randomslugfield
```

##Install

To enable `randomslugfield` in your project you need to add it to `INSTALLED_APPS` in your projects `settings.py` file:

```python
INSTALLED_APPS = (
     ...
     'randomslugfield',
     ...
)
```

##Usage

Import `RandomSlugField` and use it in your model:

```python
from django.db import models
from randomslugfield import RandomSlugField

class MyModel(models.Model):
    slug = RandomSlugField(length=7)
```

The `length` argument is required.

##Advanced Usage

By default randomslugfield generates its slug using these characters:

`abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`

You can optionally exclude lowercase/uppercase/digits/vowels using `exclude_lower=True`, `exclude_upper=True`, `exclude_digits=True`, `exclude_vowels=True`.

You cannot exclude all characters.

Example:

```python
class MyModel(models.Model):
    slug = RandomSlugField(length=7, exclude_lower=True)
```

The total number of unique slugs is determined by `characters^length`.

e.g.

```
62^9 = 13,537,086,546,263,552 possible slugs
62^8 = 218,340,105,584,896 possible slugs
62^7 = 3,521,614,606,208 possible slugs
62^6 = 56,800,235,584 possible slugs
62^5 = 916,132,832 possible slugs
```
