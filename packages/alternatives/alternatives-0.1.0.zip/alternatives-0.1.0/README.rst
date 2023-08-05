
***********************
Alternatives api
***********************

Alternatives basics
---------------------

Alternatives api is just a syntax sugar for selecting alternative variants from some set of values.
The main thing is alternative class that implements late call on callbacks.
This allow to apply boolean logic on callbacks without being executed::

    a1 = Alternative(lambda: a)
    b1 = Alternative(lambda: b)

    a_b = a1 | b1
    assert isinstance(a_b, Alternative)
    assert bool(a_b) is (a or b)

Also you can note, in the example above, that alternative can provide python truth when it's needed by
calling callbacks and evaluating boolean expressions.

Alternatives usage
---------------------

How it may be used::

    package(one_of({
        os_centos() or os_windows(): 'php',
        os_ubuntu(): 'php5'
    }))


Here one of values will be selected: php or php5.

Alternative is object, that's why we can use it as dictionary key.

In the example above you can see one_of() method:

.. automodule:: pywizard.api
   :members: one_of
   :imported-members:

Another style of evaluating alternatives is all_of:

.. automodule:: pywizard.api
   :members: all_of
   :imported-members:

And nobody restrict you from creating your own alternatives selection style.
Use source of one_of, all_of as reference.

Checks declaration
-----------------------------

*Check* is just a python function that return boolen with added annotation on it::

    @alternative
    def os_linux():
        """
        os_linux()
        Checks if it is linux-like os.
        """
        info = os_info()
        return 'linux' in info['platform']

.. note::
    As function is annotated there is some extra work needed to provide correct documentation for this function.
    @alternative handles copying __doc__ transparently for your function. But, you should take care
    of specifying correct method signature in first line of docstring.

