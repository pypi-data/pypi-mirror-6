TODO
====

- Fix ``property.mio`` example and basic data descriptors.
- Fix ``Object super()``. Make it a builtin.
- Make deleting (**unusing**) triats from an object possible again? What's the use case? jer seems to think there is no valid use-case.

- Deal with this better and raise a better error instead of crashing.

::
    
    x = method(1 + 1, a, b,
        a + b
    )
    
- Fix user errors.
- Implement ``__slice__``, ``slice(...)`` and ``xs[start:[end][:step]``

- Change the way methods and blocks are bound and unifiy them into a single entity.

  - Unified method: ``method(...)``.
  - Can be dynamically bound to objects.
  - Is always passed it's bound object as the first parameter ``self``.
  - Are by default bound to the context they are created in.

- Fix keyword argument(s) parameters.
- Bring test coverage back up to 100%
- Figure out a way to avoid recursion so ``loop(print("foo"))`` works as expected.
- Write a testing framework for mio in mio.
- Implement a "trace" hook into the interpreter. i.e: Python's ``sys.settrace()``
- Implement a basic debugger.
- Implement a basic coverage tool.
- Add ``__doc__`` (*doc strings*) support.
- Implement a basic help system.
- Do a refresher on how to write an interpreter in RPython and write a really really simple one:

  - http://doc.pypy.org/en/latest/coding-guide.html#restricted-python
  - http://morepypy.blogspot.com.au/2011/04/tutorial-writing-interpreter-with-pypy.html
