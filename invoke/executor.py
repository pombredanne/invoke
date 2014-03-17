from .context import Context
from .util import debug


class Executor(object):
    """
    An execution strategy for Task objects.

    Subclasses may override various extension points to change, add or remove
    behavior.
    """
    def __init__(self, collection, context=None):
        """
        Initialize executor with handles to a task collection & config context.

        The collection is used for looking up tasks by name and
        storing/retrieving state, e.g. how many times a given task has been run
        this session and so on. It is optional; if not given a blank `.Context`
        is used.

        A copy of the context is passed into any tasks that mark themselves as
        requiring one for operation.
        """
        self.collection = collection
        self.context = context or Context()

    def execute(self, name, kwargs=None, dedupe=True):
        """
        Execute a named task, honoring pre- or post-tasks and so forth.

        :param name:
            A string naming which task from the Executor's `.Collection` is to
            be executed. May contain dotted syntax appropriate for calling
            namespaced tasks, e.g. ``subcollection.taskname``.

        :param kwargs:
            A keyword argument dict expanded when calling the requested task.
            E.g.::

                executor.execute('mytask', {'myarg': 'foo'})

            is (roughly) equivalent to::

                mytask(myarg='foo')

        :param dedupe:
            Ensures any given task within ``self.collection`` is only run once
            per session. Set to ``False`` to disable this behavior.

        :returns:
            The return value of the named task -- regardless of whether pre- or
            post-tasks are executed.
        """
        kwargs = kwargs or {}
        # Expand task list
        task = self.collection[name]
        debug("Executor is examining top level task %r" % task)
        task_names = list(task.pre) + [name]
        # TODO: post-tasks
        debug("Task list, including pre/post tasks: %r" % (task_names,))
        # Dedupe if requested
        if dedupe:
            debug("Deduplication is enabled")
            # Compact (preserving order, so not using list+set)
            compact_tasks = []
            for tname in task_names:
                if tname not in compact_tasks:
                    compact_tasks.append(tname)
            debug("Task list, obvious dupes removed: %r" % (compact_tasks,))
            # Remove tasks already called
            tasks = []
            for tname in compact_tasks:
                if not self.collection[tname].called:
                    tasks.append(tname)
            debug("Task list, already-called tasks removed: %r" % (tasks,))
        else:
            debug("Deduplication is DISABLED, above task list will run")
            tasks = task_names
        # Execute
        results = {}
        for tname in tasks:
            t = self.collection[tname]
            debug("Executing %r" % t)
            args = []
            if t.contextualized:
                context = self.context.clone()
                context.update(self.collection.configuration(tname))
                args.append(context)
            results[t] = t(*args, **kwargs)
        return results[task]
