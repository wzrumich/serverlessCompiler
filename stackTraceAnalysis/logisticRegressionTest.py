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
File lr.py line 38, in dataset_minmax
  return minmax 
File lr.py line 139, in main
 dataset_minmax(dataset)
File lr.py, line 149, in <module> 
main()
""",
"""
File lr.py, line 147, in main
return
File lr.py, line 91, in evaluate_algorithm
return 
File lr.py, line 71, in accuracy_metric
return 
File lr.py, line 89, in evaluate_algorithm
accuracy_metric(actual, predicted)
File lr.py, line 127, in logistic_regression 
return
File lr.py, line 101, in predict
return 1.0 / (1.0 + exp(-yhat))
File lr.py, line 124, in logistic_regression 
predict(row, coef)
File lr.py, line 115, in coefficients_sgd,
return 
File lr.py, line 100, in predict
return 1.0 / (1.0 + exp(-yhat))
File lr.py, line 109, in coefficients_sgd,
predict(row, coef)
File lr.py, line 122, in logistic_regression 
 coefficients_sgd(train, l_rate, n_epoch)
File lr.py, line 87, in evaluate_algorithm
 logistic_regression(train_set, test_set, l_rate, n_epoch)
File lr.py, line 145, in main 
  evaluate_algorithm(dataset,logistic_regression,n_folds,l_rate,n_epoch)
File lr.py, line 149, in <module> 
main()
"""

]

stackTraceAnalysis.stackTraceCodeMapper(stacktraces, "/Users/ishaanpota/Desktop/serverlessCompiler/inliner/inlineTest/lr.py",[])