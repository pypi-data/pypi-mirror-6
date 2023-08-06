Mini Test
=========

This project is inspired by Ruby minispec, but now it just implement
some methods including:

::

    must_equal, must_true, must_raise.

And some other useful functions:

::

    p, pp, length, size.

github: https://github.com/jichen3000/minitest

pypi: https://pypi.python.org/pypi/minitest

--------------

Author
~~~~~~

Colin Ji jichen3000@gmail.com

How to use
~~~~~~~~~~

install:

::

    pip instsall minitest

code:

::

    if __name__ == '__main__':
        # import the minitest
        from minitest import *

        import operator

        # declare a variable for test
        tself = get_test_self()
        # you could put all your test variables on tself
        # just like declare your variables on setup.
        tself.jc = "jc"

        # declare a test
        with test("test must_equal"):
            tself.jc.must_equal('jc')
            None.must_equal(None)

        with test("test must_true"):
            True.must_true()
            False.must_true()

        # using a funcation to test equal.
        with test("test must_equal_with_func"):
            (1).must_equal(1, key=operator.eq)
            (1).must_equal(2, key=operator.eq)

        def div_zero():
            1/0
            
        # test exception
        with test("test must_raise"):
            (lambda : div_zero()).must_raise(ZeroDivisionError)
            (lambda : div_zero()).must_raise(ZeroDivisionError, "integer division or modulo by zero")
            (lambda : div_zero()).must_raise(ZeroDivisionError, "in")

result:

::

    Running tests:

    .FFF

    Finished tests in 0.013165s.

    1) Failure:
    The line No is [/Users/Colin/work/minitest/minitest/with_test.py:174]:
    --- expected
    +++ actual
    -[True]
    #[False]

    2) Failure:
    The line No is [/Users/Colin/work/minitest/minitest/with_test.py:179]:
    --- expected
    +++ actual
    -[2]
    #[1]

    3) Failure:
    The line No is [/Users/Colin/work/minitest/minitest/with_test.py:188]:
    --- expected
    +++ actual
    -['in']
    #['integer division or modulo by zero']

    4 tests, 9 assertions, 3 failures, 0 errors.
    [Finished in 0.1s]

Other useful function
~~~~~~~~~~~~~~~~~~~~~

p, pp, length, size, these four functions could been used by any object.

p is a print function. This function will add variable name as the
title. code:

::

    value = "Minitest"
    # add a title 'value : ' automatically.
    value.p()                       # value : Minitest

    # or you can give a string as title.
    value.p("It is a value:")       # It is a value: Minitest

    # if you don't want a title, use the parameter
    value.p(auto_get_title=False)   # Minitest

pp is another print function which will invoke the pprint.pprint
function. Its parameters are just like the p. code:

::

    value = "Minitest"
    value.pp()                      # value :
                                    # 'Minitest'
                                    
    value.pp("It is a value:")      #  It is a value:
                                    # 'Minitest'
                                    
    value.pp(auto_get_title=False)  # 'Minitest'

length and size will invoke len function for the caller's object. code:

::

    [1,2].length()                  # 2, just like len([1,2])
    (1,2).size()                    # 2, just like len((1,2))

