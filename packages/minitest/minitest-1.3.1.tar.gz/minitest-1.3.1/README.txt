Mini Test
=========

This project is inspired by Ruby minispec, but now it just implement
some methods including:

::

    must_equal, must_true, must_false, must_raise.

And some other useful functions:

::

    p, pp, pl, ppl, length, size, inject.

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

    pip install minitest

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

        with test("test must_false"):
            True.must_false()
            False.must_false()

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

    .FFFF.

    Finished tests in 0.013165s.

    1) Failure:
    File "/Users/Colin/work/minitest/test.py", line 29, in <module>:
    EXPECTED: True
      ACTUAL: False


    2) Failure:
    File "/Users/Colin/work/minitest/test.py", line 32, in <module>:
    EXPECTED: False
      ACTUAL: True


    3) Failure:
    File "/Users/Colin/work/minitest/test.py", line 38, in <module>:
    EXPECTED: 2
      ACTUAL: 1


    4) Failure:
    File "/Users/Colin/work/minitest/test.py", line 47, in <module>:
    EXPECTED: 'in'
      ACTUAL: 'integer division or modulo by zero'


    6 tests, 14 assertions, 4 failures, 0 errors.
    [Finished in 0.1s]

Other useful function
~~~~~~~~~~~~~~~~~~~~~

p, pp, pl, ppl, length, size, these four functions could been used by
any object.

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

pl is another print function which will print the file path and line NO.
And some editors support to go to the line of that file, such as
Sublime2. Its parameters are just like the p. Notice, it will print new
line firstly, since in some case, there will be other string before file
path, which cause some editor cannot jump to the location.

code:

::

    value = "Minitest"
    value.pl()                      #     
                                    #     File "/Users/Colin/work/minitest/test.py", line 72
                                    # value : Minitest
                                    
    value.pl("It is a value:")      #     
                                    #     File "/Users/Colin/work/minitest/test.py", line 73
                                    #  It is a value: Minitest
                                    
    value.pl(auto_get_title=False)  #     
                                    #     File "/Users/Colin/work/minitest/test.py", line 74
                                    # Minitest

ppl is another print function which will print the file path and line
NO. It almost like pl except print value in another new line. Notice, it
will print new line firstly. code:

::

    value = "Minitest"
    value.ppl()                     #     
                                    #     File "/Users/Colin/work/minitest/test.py", line 76
                                    # value :
                                    # 'Minitest'
                                    
    value.ppl("It is a value:")     #     
                                    #     File "/Users/Colin/work/minitest/test.py", line 77
                                    #  It is a value:
                                    # 'Minitest'
                                    
    value.ppl(auto_get_title=False) #     
                                    #     File "/Users/Colin/work/minitest/test.py", line 78
                                    # 'Minitest'

length and size will invoke len function for the caller's object. code:

::

    [1,2].length()                  # 2, just like len([1,2])
    (1,2).size()                    # 2, just like len((1,2))

inject\_customized\_must\_method or inject function will inject the
function which you customize. Why do I make this function? Since in many
case I will use numpy array. When it comes to comparing two numpy array,
I have to use:

::

    import numpy
    numpy.array([1]).must_equal(numpy.array([1.0]), numpy.allclose)

For being convient, I use inject\_customized\_must\_method or inject
function like:

::

    import numpy
    inject(numpy.allclose, 'must_close')
    numpy.array([1]).must_close(numpy.array([1.0]))

