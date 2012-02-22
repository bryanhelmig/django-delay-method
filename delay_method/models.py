from django.db import models


class DelayedMethodModel(models.Model):
    """
    This is a mixin that lets you 

        instance = Model.objects.get(id=1)

        # normally you'd do...
        result = instance.calculate('primes', max=1000000000)
        # sync lock....

        # but you can move it off task like so...

        task = instance.call_delay('calculate', 'primes', max=1000000000)
        # continue....
        result = task.wait()
    """

    def call_delay(self, method, *args, **kwargs):
        """
        Runs the method in the background.
        """
        from delay_method.tasks import DelayModelMethodTask

        if not callable(getattr(self, method, None)):
            raise Exception('Method "{0}" on Folder is not callable.'\
                                                            .format(method))

        return DelayModelMethodTask.delay(
                            self.__class__, self.id, method, args, kwargs)

    class Meta:
        abstract = True