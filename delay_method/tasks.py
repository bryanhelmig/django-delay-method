from celery.task import Task


class DelayModelMethodTask(Task):
    """
    Run model methods in the background.
    """
    def run(self, Model, instance_id, method, 
                                _args, _kwargs, *args, **kwargs):
        if method == 'call_delay':
            raise Exception('Cannot call to delay self again.')

        instance = Model.objects.get(id=instance_id)

        func = getattr(instance, method, None)

        if not callable(func):
            raise Exception('Method "{0}" on {1} is not callable.'\
                    .format(method, Model.__name__))

        return func(*_args, **_kwargs)
