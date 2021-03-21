"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var python_parser_1 = require("../python-program-analysis/src/python-parser");
var control_flow_1 = require("../python-program-analysis/src/control-flow");
var data_flow_1 = require("../python-program-analysis/src/data-flow");
var printNode_1 = require("../python-program-analysis/src/printNode");
//This class is meant to represent one compute block for the code
var Compute = /** @class */ (function () {
    function Compute() {
        this.statementsInComputeBlock = new Array();
    }
    Compute.prototype.addCode = function (codeBlock, hint) {
        this.statementsInComputeBlock.push([codeBlock, hint]);
    };
    //Checks if the current statement writes to a variable that is being read in the compute block, in this case, there is a WAR dependency
    Compute.prototype.writeAfterRead = function (defs) {
        for (var i = 0; i < defs.length; i++) {
            for (var j = 0; j < this.statementsInComputeBlock.length; j++) {
                var currStatement = this.statementsInComputeBlock[j];
                //console.log(currStatement)
                if (currStatement[0].type === "assign") {
                    for (var k = 0; k < currStatement[0].sources.length; k++) {
                        if (currStatement[0].sources[k].type == 'binop') {
                            var binop = currStatement[0].sources[k];
                            if (binop.left.type == 'name') {
                                if (defs[i].name == binop.left.id) { //This is saying that current statement is read on the left side of a binary operation
                                    //console.log("Caught the WAR dependence")
                                    return 1;
                                }
                            }
                            if (binop.right.type == 'name') {
                                if (defs[i].name == binop.right.id) { //This is saying that current statement is read on the right side of a binary operation
                                    //console.log("Caught the WAR dependence")
                                    return 1;
                                }
                            }
                        }
                        if (currStatement[0].sources[k].type == 'name') {
                            var nameOfVariableRead = currStatement[0].sources[k];
                            //console.log(nameOfVariableRead.id)
                            if (defs[i].name == nameOfVariableRead.id) { //This is basically saying a variable read by the current statement is being assigned in the compute block
                                //console.log("Caught the WAR dependence")
                                return 1;
                            }
                        }
                    }
                }
            }
        }
        return 0;
    };
    //Check if a statement in this compute block already wrote to a variable that this statement is writing to 
    Compute.prototype.writeAfterWrite = function (defs) {
        for (var i = 0; i < defs.length; i++) {
            for (var j = 0; j < this.statementsInComputeBlock.length; j++) {
                var currStatement = this.statementsInComputeBlock[j];
                if (currStatement[0].type === "assign") {
                    for (var k = 0; k < currStatement[0].targets.length; k++) {
                        if (currStatement[0].targets[k].type == 'name') {
                            var nameOfVariableAssigned = currStatement[0].targets[k];
                            if (defs[i].name == nameOfVariableAssigned.id) { //This is basically saying a variable read by the current statement is being assigned in the compute block
                                //console.log("Caught the WAW dependence")
                                return 1;
                            }
                        }
                    }
                }
            }
        }
        return 0;
    };
    //Meant to check if the current statement is reading anything that was written or assigned in this compute block(This forms a RAW dependency)
    Compute.prototype.readAfterWrite = function (uses) {
        for (var i = 0; i < uses.length; i++) {
            for (var j = 0; j < this.statementsInComputeBlock.length; j++) {
                var currStatement = this.statementsInComputeBlock[j];
                if (currStatement[0].type === "assign") {
                    for (var k = 0; k < currStatement[0].targets.length; k++) {
                        if (currStatement[0].targets[k].type == 'name') {
                            var nameOfVariableAssigned = currStatement[0].targets[k];
                            if (uses[i].name == nameOfVariableAssigned.id) { //This is basically saying a variable read by the current statement is being assigned in the compute block
                                //console.log("Caught the RAW dependence")
                                return 1;
                            }
                        }
                    }
                }
            }
        }
        return 0;
    };
    Compute.prototype.checkDependency = function (defs, uses) {
        return this.writeAfterRead(defs) || this.readAfterWrite(uses) || this.writeAfterWrite(defs);
    };
    Compute.prototype.displayCode = function () {
        console.log("In the display method");
        for (var i = 0; i < this.statementsInComputeBlock.length; i++) {
            console.log(printNode_1.printNode(this.statementsInComputeBlock[i][0]));
        }
    };
    return Compute;
}());
//Check if two compute blocks have any depdencies on each other, important for folding dependent compute blocks together
function computeBlockCompare(block1, block2) {
    y = new data_flow_1.DefUse();
    var genSet1 = new data_flow_1.RefSet();
    var flag1 = 0;
    for (var i = 0; i < block2.statementsInComputeBlock.length; i++) {
        y = analyzer.getDefUseForStatement(block2.statementsInComputeBlock[i][0], genSet1);
        flag1 = block1.checkDependency(y.defs.items, y.uses.items);
        if (flag1 == 1) {
            return 1;
        }
    }
    var flag2 = 0;
    return flag1 || flag2;
}
var fs = require('fs');
try {
    var data = fs.readFileSync('pythonCode.py', 'utf8');
}
catch (e) {
    console.log('Error:', e.stack);
}
var tree = python_parser_1.parse(data);
var cfg = new control_flow_1.ControlFlowGraph(tree);
var analyzer = new data_flow_1.DataflowAnalyzer();
var computeBlockArray = new Array();
var computeOne = new Compute();
computeBlockArray.push(computeOne);
var y = new data_flow_1.DefUse();
var genSet1 = new data_flow_1.RefSet();
var loopHeadFlag = 0;
var loopHeadComputeBlockIndex = -1;
var loopBody = 0;
var needNewComputeBlockFlag = 0;
//Approach 1: Take the CFG and examine each control flow block. If the block has dependencies in a certain group, put it in that group otherwise in a new group
//Problem: While loops and such are annotated in the block and you lose that information if you do it like this 
for (var i = 0; i < cfg.blocks.length; i++) {
    //console.log("block is \n" + cfg.blocks[i].hint)
    if (cfg.blocks[i].hint == "while loop head") {
        loopHeadFlag = 1;
    }
    if (cfg.blocks[i].hint == "while body") {
        loopBody = 1;
    }
    if (cfg.blocks[i].hint == "for loop head") {
        loopHeadFlag = 1;
    }
    if (cfg.blocks[i].hint == "for body") {
        loopBody = 1;
    }
    for (var j = 0; j < cfg.blocks[i].statements.length; j++) {
        //console.log("Block number" + i.toString())
        var currStatement = cfg.blocks[i].statements[j];
        //console.log(printNode(currStatement))
        y = analyzer.getDefUseForStatement(currStatement, genSet1);
        //console.log(y.defs.items)
        if (i == 0) {
            computeBlockArray[0].addCode(currStatement, ""); //Basically, add all the code for the first block to the first compute block 
        }
        else if (loopBody) {
            computeBlockArray[loopHeadComputeBlockIndex].addCode(currStatement, "loop Body");
        }
        else {
            for (var l = 0; l < computeBlockArray.length; l++) {
                var flag = computeBlockArray[l].checkDependency(y.defs.items, y.uses.items);
                if (flag == 1) {
                    if (loopHeadFlag == 1) {
                        computeBlockArray[l].addCode(currStatement, "while"); //Add code into the same compute block
                        loopHeadComputeBlockIndex = l; //future proofing code when there is an array of compute blocks. This remembers which compute block the head was in, and just puts the body in the same compute block
                        loopHeadFlag = 0;
                    }
                    else {
                        computeBlockArray[l].addCode(currStatement, ""); //Add code into the same compute block
                    }
                    needNewComputeBlockFlag = 1;
                    flag = 0;
                    break;
                }
            }
            if (needNewComputeBlockFlag === 0) {
                var cnew = new Compute();
                cnew.addCode(currStatement, "");
                computeBlockArray.push(cnew);
            }
            needNewComputeBlockFlag = 0;
        }
    }
    loopBody = 0;
}
//Some Code may get stuck in a stray compute block, rework once 
var flag1 = 0;
var flag2 = 0;
for (var f = 0; f < computeBlockArray.length; f++) {
    for (var n = f + 1; n < computeBlockArray.length; n++) {
        flag1 = computeBlockCompare(computeBlockArray[f], computeBlockArray[n]);
        flag2 = computeBlockCompare(computeBlockArray[n], computeBlockArray[f]);
        console.log(n);
        if (flag1) {
            for (var i = 0; i < computeBlockArray[n].statementsInComputeBlock.length; i++) {
                computeBlockArray[f].statementsInComputeBlock.push(computeBlockArray[n].statementsInComputeBlock[i]);
            }
            computeBlockArray.splice(n, 1);
        }
        else if (flag2) {
            console.log("Removing F");
            for (var i = 0; i < computeBlockArray[f].statementsInComputeBlock.length; i++) {
                computeBlockArray[n].statementsInComputeBlock.push(computeBlockArray[f].statementsInComputeBlock[i]);
            }
            computeBlockArray.splice(f, 1);
            n = f;
            console.log("The value of n is now:" + n);
        }
    }
}
//Print out the final compute blocks
for (var f = 0; f < computeBlockArray.length; f++) {
    console.log("The block number is " + f.toString());
    for (var n = 0; n < computeBlockArray[f].statementsInComputeBlock.length; n++) {
        console.log((computeBlockArray[f].statementsInComputeBlock[n][0]));
    }
}
//Now that we have the compute blocks, the only feasible thing to do is reconstruct the CFG on the syntax level to create separate python programs for each block
//Approach 1: Use "getSuccessor and getPredecessor"
//Approach 2: Use annotation on the statement
//Logic 
//Add code to rearrange the blocks in the right order before 
//Code to add blocks into a new file
console.log("Phase 2 begins here");
var fileCode = [];
for (var x = 0; x < computeBlockArray.length; x++) {
    for (var i = 0; i < computeBlockArray[x].statementsInComputeBlock.length; i++) {
        var hint = computeBlockArray[x].statementsInComputeBlock[i][1];
        var node = computeBlockArray[x].statementsInComputeBlock[i][0];
        //console.log(printNode(computeBlockArray[x].statementsInComputeBlock[i][0]) + computeBlockArray[x].statementsInComputeBlock[i][1])
        console.log("here2");
        if (hint == "") {
            console.log("here1");
            try {
                fileCode.push(printNode_1.printNode(node));
            }
            catch (_a) {
                console.log("herewtf");
                continue;
            }
            finally {
            }
        }
        else {
            if (hint == "while") {
                fileCode.push("while " + printNode_1.printNode(node) + ":");
                for (var j = i + 1; j < computeBlockArray[2].statementsInComputeBlock.length; j++) {
                    if (computeBlockArray[2].statementsInComputeBlock[j][1] == "loop Body") {
                        fileCode.push("\t" + printNode_1.printNode(computeBlockArray[2].statementsInComputeBlock[j][0]));
                    }
                }
            }
        }
    }
    fs.writeFileSync("block" + x.toString() + ".py", fileCode.join("\n"));
    fileCode = [];
}
