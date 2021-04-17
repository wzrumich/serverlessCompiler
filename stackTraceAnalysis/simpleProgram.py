import sys
import traceback

import stackTraceAnalysis
#import
def call1():
    z = 4
    call4()
    f = z


def call2():
    # Code Block 1
    f()
    # Code Block 2


def call3():
    print("Hello")


def call4():
    print("here")
    y = 9
    x = 0
    summary = traceback.StackSummary.extract(traceback.walk_stack(None))
    stackTraceAnalysis.stackTraceCodeMapper(
        ''.join(summary.format()), 'simpleProgram.py')
    return x
def f():

    # some code here

    # summary = traceback.StackSummary.extract(traceback.walk_stack(None))
    # stackTraceAnalysis.stackTraceCodeMapper(
    #     ''.join(summary.format()), 'pythonCode.py')
    print("hi")
    # some code here



def main():
    print("wtaf")
    call1()


main()




