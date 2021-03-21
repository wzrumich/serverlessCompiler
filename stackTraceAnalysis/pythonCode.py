import sys
import traceback
import stackTraceAnalysis
# importing the modules


def call1(f):

    # Code Block 1

    call2(f)

    # Code Block 2


def call2(f):

    # Code Block 1

    f()

    # Code Block 2


def call3():
    print("Hello")


def call4():
    x = 8 * 7
    return x


def f():

    # some code here

    summary = traceback.StackSummary.extract(traceback.walk_stack(None))
    stackTraceAnalysis.stackTraceCodeMapper(
        ''.join(summary.format()), 'pythonCode.py')

    # some code here


call1(f)
