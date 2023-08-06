Tastypie Queryset Client
========================

Client for [Tastypie](https://github.com/toastdriven/django-tastypie). Provide operation similar to the Django Model API .

This is a fork of original project modified to run under python >=3.3

Usage
=====

Get
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> client.your.objects.get(name="your")
<your: {u"id": u"1", u"name": u"your", u"status": u"any"}>
```

Count
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> client.your.objects.count()
100
```

Filter
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> client.your.objects.filter(name="your")
<QuerySet <class 'Response'> (3/3)>
```

Save
----
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> your = client.your(name="name")
>>> your
<your: {u"name": u"name"}>
>>> your.save()  # save Your object.
>>> your
<your: {u"id": u"2", u"name": u"name"}>
```

Delete
------
```python
>>> client = Client("http://api.server.com/your/v1/")
>>> message = client.message(subject="subject delete 1", body="body delete 1")
>>> message.save()
>>> message.id
<message: {u"id": u"1", u"subject": u"subject delete 1", u"body": u"body delete 1"}>
>>> message.delete()  # remove Message object.
>>> try:
>>>     message.id
>>> except AttributeError:
>>>     assert True  # throw AttributeError.
```

Requirements
=============

Tastypie: [Over the 0.9.12-alpha](https://github.com/toastdriven/django-tastypie/commit/daca57ad5f62afcf1ffacaaf77bc3715a1b9a04f).

Setup
=====
```bash
$ pip install tastypie-queryset-client
```

Documentation
==============

[tastypie-queryset-client.readthedocs.org](http://tastypie-queryset-client.readthedocs.org)


License
=======
MIT License
