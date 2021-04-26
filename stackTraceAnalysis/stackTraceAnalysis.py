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
import re


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
    print("here")
    for anode in ast.walk(ast.parse(codeblock1)):
            
       
        if type(anode).__name__ == 'Assign':
            if type(anode.value).__name__ == 'Name':
                res1.add(anode.value.id)
            
            
        elif type(anode).__name__ == 'For':
            
            if type(anode.target).__name__ == 'Name':
                res1.add(anode.target.id)
        elif type(anode).__name__ == 'Call':
            for el in anode.args:
                if type(el).__name__ == 'Name':
                    res1.add(el.id)

        

    #print(res1)
    
    return res1

#Returns a list of variables written to code block
def variablesWrittenInCodeBlock(codeblock1):

    #Checking RAW dependencies 
    res1 = set()
    for anode in ast.walk(ast.parse(codeblock1)):
        
        if type(anode).__name__ == 'Assign':
            for t in anode.targets:
                
                if type(t).__name__ == 'Name':
                    res1.add(t.id)
        elif type(anode).__name__ == 'For':
            if type(anode.target).__name__ == 'Name':
                res1.add(anode.target.id)
            
    
    
    return res1

    




# Objective: Given a list of stack traces corresponding to different phases in the program, map these stack traces to regions in the code and generate separate code for those blocks
# Then, analayze the dependencies between them and replace those with RDMA calls


def stackTraceCodeMapper(stacktraces, filename, remoteVars):

    # Step 1: Use stacktrace to create compute blocks:

    # Question, how do you handle code before the first call in the stack
    fp = open(filename)
    lines = fp.readlines()


    linesRequiredOverall = []
    computeBlocks = []
    computeBlocksInlined = []



    for stacktrace in stacktraces:
        # split stack trace into individual lines
        tokenizedTrace = (stacktrace.split("File"))

        lineNumbersRequiredPerBlock = []

        last_method_def = ""

        curr_method = ""

        # Extract code mentioned in the stack trace from the source code, new approach, do this in the form of line numbers
        for i in range(len(tokenizedTrace) - 1, 0, -1):

            if i == len(tokenizedTrace) - 1:  # This adds the first function call to the compute block
                lineInd = tokenizedTrace[i].find("line")
                commaInd = tokenizedTrace[i].find(",", lineInd)
                lineNo = tokenizedTrace[i][lineInd + 5:commaInd]
                if int(lineNo) not in linesRequiredOverall:
                        lineNumbersRequiredPerBlock.append(int(lineNo))
                        linesRequiredOverall.append(int(lineNo))
                last_method_def = "main"
                curr_method = "main"
                

            elif i == 1:
                #print("finally here")
                #print(last_method_def)
                lineInd = tokenizedTrace[i].find("line")
                commaInd = tokenizedTrace[i].find(",", lineInd)
                lineNo = tokenizedTrace[i][lineInd + 5:commaInd]
                #print(lineNo)

                for j in range(0, len(lines)):

                    if lines[j].find(curr_method) != -1:
                        for l in range(j+2, int(lineNo)+1):
                            if l not in linesRequiredOverall:
                                lineNumbersRequiredPerBlock.append(l)
                                linesRequiredOverall.append(l)

            else:

                lineInd = tokenizedTrace[i].find("line")
                commaInd = tokenizedTrace[i].find(",", lineInd)
                lineNo = tokenizedTrace[i][lineInd + 5:commaInd]
                #print(lineNo)
                # We are trying to find the method that this stack trace is referring to and take the lines leading up to the function call
                #methodDef = "def " + tokenizedTrace[i].split()[-2]
                # Keep track of the method being called
                for j in range(0, len(lines)):
                    #print(lines[j])
                    #print(last_method_def)
                    #print(re.search("dataset_minmax",lines[j]))
                    if re.search(curr_method,lines[j]) != None:                  
                        for l in range(j + 2, int(lineNo)):
                            if l not in linesRequiredOverall:
                                lineNumbersRequiredPerBlock.append(l)
                                linesRequiredOverall.append(l)


                if(tokenizedTrace[i].find("return") != -1):
                    curr_method = last_method_def
                    
                else:
                    last_method_def = curr_method
                    curr_method = tokenizedTrace[i].split()[-1]
                    curr_method = curr_method[:curr_method.find("(")]
        

        computeBlocks.append(lineNumbersRequiredPerBlock)
            
    fp.close()
   

    #Part 2: In Progress: Use the mapping function in the inliner to find the location of the compute block in the inlined code
    s2_out = subprocess.check_output([sys.executable, "/Users/ishaanpota/Desktop/serverlessCompiler/inliner/inline.py"])
    inlineOutput = str(s2_out, 'utf-8')

    lineMap = json.loads(inlineOutput.split('\n')[::-1][1])


    #Note that a function can be called multiple times, so the lineMap is going to a map a line in the old code to a list of lines in the new code,
    #currently treating it like a number

    

    for computeBlock in computeBlocks:
        newLineNos = []
        for lineNo in computeBlock:
            if str(lineNo) in lineMap.keys():
                newLineNos.append(lineMap[str(lineNo)][0])
        
        computeBlocksInlined.append(newLineNos)


    #print(computeBlocksInlined)
    #print(lineMap.keys())

    for j in range(0,len(computeBlocksInlined)):
        for i in computeBlocksInlined[j]:
            if i+2 in computeBlocksInlined[j] and i+1 not in computeBlocksInlined[j]:
                computeBlocksInlined[j].append(i+1)
        
        if j+1 <len(computeBlocksInlined) and max(computeBlocksInlined[j]) - min(computeBlocksInlined[j+1]) == -2:
            computeBlocksInlined[j].append((max(computeBlocksInlined[j]) + 1))




    #Now, use the newLineNos to separate the code into two compute blocks and do dependency analysis between them, replacing all variable accesses with remote accesses
    inlinedCode = open("/Users/ishaanpota/Desktop/serverlessCompiler/stackTraceAnalysis/inlinedCode.py","r")
    x = inlinedCode.readlines()
    DAG = []
    for computeBlock in computeBlocksInlined:
        computeStackTrace = ""
        counter = 1
        for line in x:
            if line.find("import") != -1:
                computeStackTrace +=line
        computeStackTrace += "def main():" + "\n" 
        for line in x:
            if counter in computeBlock:
                computeStackTrace +=  line 
            counter +=1
        DAG.append(computeStackTrace)

    


    
    



    #Order the compute blocks 
    #To order the compute blocks, we will just use the line numbers to figure out which block goes before which 


    #add code to handle dependent variables across compute blocks


    #for all compute blocks:



    for i in range(0,len(DAG)):

        varWrittenList = []
        varWrittenList = variablesWrittenInCodeBlock(DAG[i])
        print(i)
        print("Data for this block")
        print("The variables written in this block are")
        print(varWrittenList)
        remoteWriteVars = []

        for var in varWrittenList:
            if var in remoteVars:
                remoteWriteVars.append(var)

        varReadList = []
        varReadList = variablesReadInCodeBlock(DAG[i])
        remoteReadVars = []
        print("The variables read in this block are")
        print(varReadList)


       

        for var in varWrittenList:
            if var in remoteVars: #Automatically adds the vars the user has decided to be remote
                remoteWriteVars.append(var)



        for j in range(i+1,len(DAG)):
            varReadListInner = []
            varReadListInner = variablesReadInCodeBlock(DAG[j])
        
            for var in varReadListInner:
                if var in varWrittenList:
                    remoteWriteVars.append(var)

        

        for k in range(i-1,-1,-1):
            varWriteListInner = []
            varWriteListInner = variablesWrittenInCodeBlock(DAG[k])

            for var in varWriteListInner:
                if var in varReadList:
                    remoteReadVars.append(var)

        
        
        print("========")
        s = ""


        finalComputeBlock = ""

        for j in range(0,len(remoteReadVars)):
            if remoteReadVars[j] in remoteVars:
                s += remoteReadVars[j] + " = "
            s += remoteReadVars[j] + " = " + "context_dict[\"" + remoteReadVars[j] + "\"]" + "\n"
            if j != len(remoteReadVars) -1:
                s += "    "


        


        codeRead =  ("""    action = buffer_pool_lib.action_setup()\n    transport_name = 'client1'\n    trans = action.get_transport(transport_name, 'rdma')\n    trans.reg(buffer_pool_lib.buffer_size)\n    buffer_pool = buffer_pool_lib.buffer_pool(trans, context_dict["buffer_pool_metadata"])""" + "\n    " + s)

        insertPoint = DAG[i].find(":") + 2

        newStr = DAG[i][:insertPoint] + codeRead + DAG[i][insertPoint:]


        if(len(remoteReadVars) > 0):
            DAG[i] = newStr

        

        r = ""


        for k in range(0,len(remoteWriteVars)):
            if remoteWriteVars[k] in remoteVars:
                r += "    " + "remote_" + remoteWriteVars[k] + "=" + "remote_array(buffer_pool, input_ndarray=" + remoteWriteVars[k] + ")"
                r+= "    " + "remote_" + remoteWriteVars[k] + "_metadata" + "=" + "remote_" + remoteWriteVars[k] + ".get_array_metadata()"
                r += "    " + "context_dict[\"" + remoteWriteVars[k] + "\"]" + "=" + "remote_" + remoteWriteVars[k] + "_metadata"
            else:
                r += "    " + "context_dict[\"" + remoteWriteVars[k] + "\"]" + "=" + remoteWriteVars[k] + "\n"
        
        #print(r)

        


        


        codeWrite =  r + """    context_dict["buffer_pool_metadata"] = buffer_pool.get_buffer_metadata()\n    buffer_pool_lib.write_params(context_dict)"""


        if(len(remoteWriteVars) > 0):
            DAG[i] += codeWrite



        #print(DAG[i])
        blockName = "app" + str(i) + ".py"
        f = open(blockName, "a")
        f.write(DAG[i])
        f.close()




           






    

    



    






    

    

   


