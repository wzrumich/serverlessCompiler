import sys
sys.path.insert(1, '/Users/ishaanpota/Desktop/serverlessCompiler/inliner')

from symbolHelper import *
from visitor import *
import copy
import pprint
import astunparse
import astor
import utils
import astpretty
import ast
import traceback
import subprocess
import json


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




def variablesReadInCodeBlock(codeblock1):
    #Checking RAW dependencies 
    res1 = set()
    for anode in ast.walk(ast.parse(codeblock1)):
    
        
        if type(anode).__name__ == 'Assign':
            if type(anode.value).__name__ == 'Name':
                print(anode.value.id)
                res1.add(anode.value.id)
                
            
            
        elif type(anode).__name__ == 'For':
            if type(anode.target).__name__ == 'Name':
                res1.add(anode.target.id)

    #print(res1)
    
    return res1

#Returns a list of variables written to code block
def variablesWrittenInCodeBlock(codeblock1):

    #Checking RAW dependencies 
    res1 = set()
    for anode in ast.walk(ast.parse(codeblock1)):
        
        if type(anode).__name__ == 'Assign':
            
            res1.update(t.id for t in anode.targets if type(t).__name__ == 'Name')
        elif type(anode).__name__ == 'For':
            if type(anode.target).__name__ == 'Name':
                res1.add(anode.target.id)
    
    
    return res1

    




# Objective: Given a list of stack traces corresponding to different phases in the program, map these stack traces to regions in the code and generate separate code for those blocks
# Then, analayze the dependencies between them and replace those with RDMA calls


def stackTraceCodeMapper(stacktrace, filename):

    # Step 1: Use stacktrace to create compute blocks:

    # Question, how do you handle code before the first call in the stack
    fp = open(filename)
    lines = fp.readlines()

    # split stack trace into individual lines
    tokenizedTrace = (stacktrace.split("File"))

    print(stacktrace)

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
                    for l in range(j+2, int(lineNo)):
                        lineNumbersRequired.append(l)

        else:

            lineInd = tokenizedTrace[i].find("line")
            commaInd = tokenizedTrace[i].find(",", lineInd)
            lineNo = tokenizedTrace[i][lineInd + 5:commaInd]
            # We are trying to find the method that this stack trace is referring to and take the lines leading up to the function call
            methodDef = "def " + tokenizedTrace[i].split()[-2]
            # Keep track of the method being called
            last_method_def = "def " + tokenizedTrace[i].split()[-1]

            for j in range(0, len(lines)):
                if lines[j].find(methodDef) != -1:
                    print(j)
                    for l in range(j + 2, int(lineNo)):
                        lineNumbersRequired.append(l)


    fp.close()
   

    #Part 2: In Progress: Use the mapping function in the inliner to find the location of the compute block in the inlined code

    newLineNos = []
    s2_out = subprocess.check_output([sys.executable, "/Users/ishaanpota/Desktop/serverlessCompiler/inliner/inline.py"])
    inlineOutput = str(s2_out, 'utf-8')

    lineMap = json.loads(inlineOutput.split('\n')[::-1][1])


    #Note that a function can be called multiple times, so the lineMap is going to a map a line in the old code to a list of lines in the new code,
    #currently treating it like a number

    for i in lineNumbersRequired:
        if str(i) in lineMap.keys():
            newLineNos.append(lineMap[str(i)][0])


    print(newLineNos)
    print(lineMap.keys())


    #Now, use the newLineNos to separate the code into two compute blocks and do dependency analysis between them, replacing all variable accesses with remote accesses
    inlinedCode = open("/Users/ishaanpota/Desktop/serverlessCompiler/stackTraceAnalysis/inlinedCode.py","r")
    computeStackTrace = ""
    computeNotStackTrace = ""

    computeStackTrace = "def main():" + "\n"


    counter = 1 

    for line in inlinedCode.readlines():
        if counter in newLineNos:
            computeStackTrace +=  line
        else:
            computeNotStackTrace += line 
        counter +=1


    
    DAG = []

    DAG.append(computeStackTrace)
    DAG.append(computeNotStackTrace)
    

    #print(computeStackTrace)
    #print(computeNotStackTrace)


    #Order the compute blocks 
    #To order the compute blocks, we will just use the line numbers to figure out which block goes before which 


    #add code to handle dependent variables across compute blocks


    #for all compute blocks:


    for i in range(0,len(DAG)):
    
        varWrittenList = []
        varWrittenList = variablesWrittenInCodeBlock(DAG[i])
        remoteWriteVars = []

        varReadList = []
        varReadList = variablesReadInCodeBlock(DAG[i])
        remoteReadVars = []



        for j in range(i,len(DAG)):
            varReadList = []
            varReadList = variablesReadInCodeBlock(DAG[j])
        
            for var in varReadList:
                if var in varWrittenList:
                    remoteWriteVars.append(var)
        

        for k in range(i-1,-1,-1):
            varWriteList = []
            varWriteList = variablesWrittenInCodeBlock(DAG[k])

            for var in varWriteList:
                if var in varReadList:
                    remoteReadVars.append(var)
        
        print(remoteReadVars)
        print(remoteWriteVars)
        print("========")
        s = ""

        for i in range(0,len(remoteReadVars)):
            s = remoteReadVars[i] + " = " + "context_dict[\"" + remoteReadVars[i] + "\"]" + "\n"


        codeRead =  ("""action = buffer_pool_lib.action_setup()\ntransport_name = 'client1'\ntrans = action.get_transport(transport_name, 'rdma')\ntrans.reg(buffer_pool_lib.buffer_size)\nbuffer_pool = buffer_pool_lib.buffer_pool(trans, context_dict["buffer_pool_metadata"])""" + "\n" + s)



        r = ""


        for i in range(0,len(remoteWriteVars)):
            r = "    " + "context_dict[\"" + remoteWriteVars[i] + "\"]" + "=" + remoteWriteVars[i] + "\n"

        #print(r)


        


        codeWrite =  r + """    context_dict["buffer_pool_metadata"] = buffer_pool.get_buffer_metadata()\n    buffer_pool_lib.write_params(context_dict)"""


        c =  codeRead + DAG[i] + codeWrite
        print(c)








            
        



            #Insert code to write the written variables to remote memory (Zerui's library calls)
           






    

    



    






    

    

   


