import sys
import traceback

import stackTraceAnalysis




stacktraces = [

"""
File lr.py, line 19, in load_csv
return dataset

File lr.py, line 135, in main
load_csv(file name)

File lr.py, line 149, in <module> 
main()

"""   
    ,
"""

File lr.py, line 60, in cross_validation_split
 return dataset_split


File lr.py, line 76, in evaluate_algorithm
 cross_validation_split(dataset,n_folds)

File lr.py, line 145, in main 
 evaluate_algorithm(dataset,logistic_regression,n_folds,l_rate,n_epoch)


File lr.py, line 46, in normalize_dataset 
 return 
 
File lr.py line 140, in main
 normalize_dataset(dataset,minmax)

File lr.py line 37, in dataset_minmax
  return minmax 

File lr.py line 139, in main
 dataset_minmax(dataset)


File lr.py, line 149, in <module> 
main()
"""]


stackTraceAnalysis.stackTraceCodeMapper(stacktraces, "/Users/ishaanpota/Desktop/serverlessCompiler/inliner/inlineTest/lr.py",[])