# django-method-delay

This is a simple way to use Celery without writing your own tasks for models. This makes it super, duper easy to port an existing legacy app to async. All you have to do is...

```python
from delay_method.models import DelayedMethodModel

class YourModel(DelayedMethodModel)
    # ...
```

...and...

```python
instance.call_delay('method_name', *args, **kwargs)
```

A demo is worth a thousand words...

### Your models.py....

```python
from django.db import models

from delay_method.models import DelayedMethodModel


class Person(DelayedMethodModel):
    added = models.DateTimeField(auto_now_add=True)
    
    name = models.CharField(max_length=100)
    skill = models.CharField(max_length=255)

    friends = models.ManyToManyField('self')
    
    def together(self):
        return '{0} is great at {1}.'.format(self.name, self.skill)
    
    def likes(self, *args):
        return '{0} likes {1}.'.format(self.name, ', '.join(args))
    
    def puts(self, **kwargs):
        puts = ' and '.join(
            ['the {0} in the {1}'.format(k,v) for k,v in kwargs.items()]
        )
        return '{0} puts {1}.'.format(self.name, puts)

    def alert_friends(self):
        for friend in self.friends.all():
            # send an email!
            pass
```

### Your view.py....

```python
from django.http import HttpResponse

from myapp.models import Person


def combine_view(request, person_id):
    """
    Collecting multiple slow to compute things to return to the
    user at the same time.
    """
    person = Person.objects.get(id=person_id)
    
    # equivalent to person.together()
    task1 = person.call_delay('together')
    
    # equivalent to person.likes('cats', 'dogs)
    task2 = person.call_delay('likes', 'cats', 'dogs')
    
    # equivalent to person.puts(dog='doghouse', cat='litter box')
    task3 = person.call_delay('puts', dog='doghouse', cat='litter box')
    
    # you'd need to collect the results....
    together, likes, puts = task1.wait(), task2.wait(), task3.wait()
    
    return HttpResponse("\n".join([together, likes, puts]))


def trigger_view(request, person_id):
    """
    Let this persons friends know something is up. We don't want to call
    person.alert_friends() directly in the request/response cycle as that 
    would be very slow to make the view wait on maybe hundreds of emails
    being sent. 
    """
    person = Person.objects.get(id=person_id)
    
    # equivalent to person.alert_friends()
    task = person.call_delay('alert_friends')
    
    return HttpResponse('Your friends will be alerted!')
```