# django-method-delay

This is a simple way to use Celery without writing your own tasks for models. This makes it super, duper easy to port an existing legacy app to async.

A demo is worth a thousand words...

### Your models.py....

	from django.db import models
    
	from delay_method.models import DelayedMethodModel
    
    
	class Person(DelayedMethodModel):
	    added = models.DateTimeField(auto_now_add=True)
        
	    name = models.CharField(max_length=100)
	    skills = models.CharField(max_length=255)
        
	    def together(self):
	        return '{0} is great at {1}.'.format(self.name, self.skills)
        
	    def likes(self, *args):
	        return '{0} likes {1}.'.format(self.name, ', '.join(args))
        
	    def puts(self, **kwargs):
	        puts = ' and '.join(
	            ['the {0} in the {1}'.format(k,v) for k,v in kwargs.items()]
	        )
	        return '{0} puts {1}.'.format(self.name, puts)

### Your view.py....

    from django.http import HttpResponse
    
    from myproject.models import Person
    
    def slow_view(request, person_id):
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