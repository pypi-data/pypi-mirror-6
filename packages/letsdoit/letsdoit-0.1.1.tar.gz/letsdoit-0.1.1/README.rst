Letsdoit
========

Lets doit_ read tasks defined using classes, decorated functions or function
calls.

A sample dodo.py file::

    from letsdoit import TaskBase, task

    # Define a task using a decorator.
    @task(file_dep=['dodo.py'])
    def simple():
        print "hi"

    # By calling a function.
    compile = task(actions=['cc -c main.c'],
                   file_dep=["main.c", "defs.h"],
                   targets=['main.o'],
                  )

    # A class with a run() method
    class hello(TaskBase):
        """Hello from Python."""
        targets = ['hello.txt']

        def run(self):
            with open(self.targets[0], "a") as output:
                output.write("Hello world.")

    # A class with a list of actions.
    class checker(TaskBase):
        """Run pyflakes."""
        actions = ['pyflakes letsdoit.py']
        file_dep = ['letsdoit.py']


.. _doit: http://pydoit.org/
