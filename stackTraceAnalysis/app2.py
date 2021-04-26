from random import seed
from random import randrange
from csv import reader
from math import exp
def main():
    action = buffer_pool_lib.action_setup()
    transport_name = 'client1'
    trans = action.get_transport(transport_name, 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)
    buffer_pool = buffer_pool_lib.buffer_pool(trans, context_dict["buffer_pool_metadata"])
    n_epoch = context_dict["n_epoch"]
    scores = context_dict["scores"]
    evaluate_algorithm_folds = virtual_return_register_2
    evaluate_algorithm_scores = list()
    for evaluate_algorithm_fold in evaluate_algorithm_folds:
        evaluate_algorithm_train_set = list(evaluate_algorithm_folds)
        evaluate_algorithm_train_set.remove(evaluate_algorithm_fold)
        evaluate_algorithm_train_set = sum(evaluate_algorithm_train_set, [])
        evaluate_algorithm_test_set = list()
        for evaluate_algorithm_row in evaluate_algorithm_fold:
            evaluate_algorithm_row_copy = list(evaluate_algorithm_row)
            evaluate_algorithm_test_set.append(evaluate_algorithm_row_copy)
            evaluate_algorithm_row_copy[(- 1)] = None
        logistic_regression_predictions = list()
        coefficients_sgd_coef = [0.0 for coefficients_sgd_i in range(len(evaluate_algorithm_train_set[0]))]
        for coefficients_sgd_epoch in range(n_epoch):
            for coefficients_sgd_row in evaluate_algorithm_train_set:
                predict_yhat = coefficients_sgd_coef[0]
                for predict_i in range((len(coefficients_sgd_row) - 1)):
                    predict_yhat += (coefficients_sgd_coef[(predict_i + 1)] * coefficients_sgd_row[predict_i])
                virtual_return_register_3 = (1.0 / (1.0 + exp((- predict_yhat))))
                coefficients_sgd_yhat = virtual_return_register_3
                coefficients_sgd_error = (coefficients_sgd_row[(- 1)] - coefficients_sgd_yhat)
                coefficients_sgd_coef[0] = (coefficients_sgd_coef[0] + l_rate)
                coefficients_sgd_coef[0] = (((coefficients_sgd_coef[0] * coefficients_sgd_error) * coefficients_sgd_yhat) * (1.0 - coefficients_sgd_yhat))
                for coefficients_sgd_i in range((len(coefficients_sgd_row) - 1)):
                    coefficients_sgd_coef[(coefficients_sgd_i + 1)] = (coefficients_sgd_coef[(coefficients_sgd_i + 1)] + ((((l_rate * coefficients_sgd_error) * coefficients_sgd_yhat) * (1.0 - coefficients_sgd_yhat)) * coefficients_sgd_row[coefficients_sgd_i]))
        virtual_return_register_4 = coefficients_sgd_coef
        logistic_regression_coef = virtual_return_register_4
        for logistic_regression_row in evaluate_algorithm_test_set:
            logistic_regression_yhat = virtual_return_register_5
            logistic_regression_yhat = round(logistic_regression_yhat)
            logistic_regression_predictions.append(logistic_regression_yhat)
        virtual_return_register_6 = logistic_regression_predictions
        evaluate_algorithm_predicted = virtual_return_register_6
        evaluate_algorithm_actual = [evaluate_algorithm_row[(- 1)] for evaluate_algorithm_row in evaluate_algorithm_fold]
        accuracy_metric_correct = 0
        for accuracy_metric_i in range(len(evaluate_algorithm_actual)):
            if (evaluate_algorithm_actual[accuracy_metric_i] == evaluate_algorithm_predicted[accuracy_metric_i]):
                accuracy_metric_correct += 1
        virtual_return_register_7 = ((accuracy_metric_correct / float(len(evaluate_algorithm_actual))) * 100.0)
        evaluate_algorithm_accuracy = virtual_return_register_7
        evaluate_algorithm_scores.append(evaluate_algorithm_accuracy)
    print(('Scores: %s' % scores))
    print(('Mean Accuracy: %.3f%%' % (sum(scores) / float(len(scores)))))
