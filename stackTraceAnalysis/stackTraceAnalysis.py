def formatMethod(method):
    method = method.split()

    finString = ""
    for i in range(0, len(method)):
        # print(method[i])
        if i == 0:
            finString += "def " + method[0] + "\n" + "\t"

        else:
            finString += method[i] + "\n" + "\t"

    finString += "\n"
    return finString


# Objective: Given a list of stack traces corresponding to different phases in the program, map these stack traces to regions in the code and generate separate code for those blocks
# Then, analayze the dependencies between them and replace those with RDMA calls


def stackTraceCodeMapper(stacktrace, filename):

    # Step 1: Use stacktrace to create compute blocks:

    # Question, how do you handle code before the first call in the stack
    fp = open(filename)
    lines = fp.readlines()

    f = open("stacktraceCode.py", "w")

    # split stack trace into individual lines
    tokenizedTrace = (stacktrace.split("File"))

    lineNumbersRequired = []

    last_method_def = ""

    # Extract code mentioned in the stack trace from the source code, new approach, do this in the form of line numbers
    for i in range(len(tokenizedTrace) - 1, 0, -1):

        if i == len(tokenizedTrace) - 1:  # This adds the first function call to the compute block
            lineInd = tokenizedTrace[i].find("line")
            commaInd = tokenizedTrace[i].find(",", lineInd)
            lineNo = tokenizedTrace[i][lineInd + 5:commaInd]
            lineNumbersRequired.append(int(lineNo))

        elif i == 1:
            lineInd = tokenizedTrace[i].find("line")
            commaInd = tokenizedTrace[i].find(",", lineInd)
            lineNo = tokenizedTrace[i][lineInd + 5:commaInd]

            for j in range(0, len(lines)):

                if lines[j].find(last_method_def) != -1:
                    for l in range(j+1, int(lineNo) + 1):
                        lineNumbersRequired.append(l)

        else:
            # print(tokenizedTrace[i].split()[-1])
            lineInd = tokenizedTrace[i].find("line")
            commaInd = tokenizedTrace[i].find(",", lineInd)
            lineNo = tokenizedTrace[i][lineInd + 5:commaInd]
            # We are trying to find the method that this stack trace is referring to and take the lines leading up to the function call
            methodDef = "def " + tokenizedTrace[i].split()[-2]
            # Keep track of the method being called
            last_method_def = "def " + tokenizedTrace[i].split()[-1]

            for j in range(0, len(lines)):
                if lines[j].find(methodDef) != -1:
                    for l in range(j, int(lineNo) + 1):
                        lineNumbersRequired.append(l)

    f.close()

    return(lineNumbersRequired)

    fp.close()


# Part 2: In Progress: Use the mapping function in the inliner to find the location of the compute block in the inlined code
