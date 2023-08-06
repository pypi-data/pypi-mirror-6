This is a simple Nose plugin that forces nosetests to print the full test name in verbose mode, rather than just the docstring.

For example, given the test file ``example.py``:

.. code-block:: python

    class MyTestCase(TestCase):

        def test_without_docstring(self):
            pass

        def test_with_docstring(self):
            """This is my docstring"""
            pass

This plugin changes the output of ``nosetests -v example.py`` from::

    This is my docstring ... ok
    test_without_docstring (vagrant.venmo_tests.example.MyTestCase) ... ok

To::

    test_with_docstring (mymodule.MyTestCase) ... ok
    test_without_docstring (mymodule.MyTestCase) ... ok


Install with ``pip install nose-description-fixer-plugin``.
