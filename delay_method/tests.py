from django.db import models
from django.test import TestCase

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


class DelayedMethodModelTest(TestCase):
    def setUp(self):
        self.billy = Person.objects.create(
            name = 'Billy Mayes',
            skills = 'yelling & selling'
        )

    def test_call_self(self):
        self.assertRaises(Exception, self.billy.call_delay, ['call_delay'])

    def test_call_delay_no_args(self):
        task = self.billy.call_delay('together')
        result = task.wait()

        self.assertEqual(result, self.billy.together())

    def test_call_delay_args(self):
        task = self.billy.call_delay('likes', 
                        'this', 'that', 'the other thing')
        result = task.wait()

        self.assertEqual(
            result,
            self.billy.likes('this', 'that', 'the other thing')
        )

    def test_call_delay_kwarg(self):
        task = self.billy.call_delay('puts', 
                        dog='doghouse', cat='litter box')
        result = task.wait()

        self.assertEqual(
            result,
            self.billy.puts(dog='doghouse', cat='litter box')
        )