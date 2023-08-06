This is a simple Nose plugin that forces nosetests to print the full test name, rather than the docstring.

For example, given the test file `example.py`::

.. code-block:: python

    class MyTestCase(TestCase):

        def test_without_docstring(self):
            pass

        def test_with_docstring(self):
        """This is my docstring"""
            pass

This plugin changes the output of `nosetests -v example.py` from::

    test_without_docstring (mymodule.MyTestCase) ... ok
    This is my docstring ... ok

To::

    test_without_docstring (mymodule.MyTestCase) ... ok
    test_with_docstring (mymodule.MyTestCase) ... ok

Installation
------------

`pip install nose-description-fixer-plugin`
