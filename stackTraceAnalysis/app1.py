from random import seed
from random import randrange
from csv import reader
from math import exp
def main():
    filename = 'pima-indians-diabetes.csv'
    dataset = virtual_return_register_0
    dataset_minmax_minmax = list()
    for dataset_minmax_i in range(len(dataset[0])):
        dataset_minmax_col_values = [dataset_minmax_row[dataset_minmax_i] for dataset_minmax_row in dataset]
        dataset_minmax_value_min = min(dataset_minmax_col_values)
        dataset_minmax_value_max = max(dataset_minmax_col_values)
        dataset_minmax_minmax.append([dataset_minmax_value_min, dataset_minmax_value_max])
    virtual_return_register_1 = dataset_minmax_minmax
    minmax = virtual_return_register_1
    for normalize_dataset_row in dataset:
        for normalize_dataset_i in range(len(normalize_dataset_row)):
            normalize_dataset_row[normalize_dataset_i] = ((normalize_dataset_row[normalize_dataset_i] - minmax[normalize_dataset_i][0]) / (minmax[normalize_dataset_i][1] - minmax[normalize_dataset_i][0]))
    n_folds = 5
    l_rate = 0.1
    n_epoch = 100
    cross_validation_split_dataset_split = list()
    cross_validation_split_dataset_copy = list(dataset)
    cross_validation_split_fold_size = int((len(dataset) / n_folds))
    for cross_validation_split_i in range(n_folds):
        cross_validation_split_fold = list()
        while (len(cross_validation_split_fold) < cross_validation_split_fold_size):
            cross_validation_split_index = randrange(len(cross_validation_split_dataset_copy))
            cross_validation_split_fold.append(cross_validation_split_dataset_copy.pop(cross_validation_split_index))
        cross_validation_split_dataset_split.append(cross_validation_split_fold)
    scores = virtual_return_register_8
    context_dict["n_epoch"]=n_epoch
    context_dict["scores"]=scores
    context_dict["buffer_pool_metadata"] = buffer_pool.get_buffer_metadata()
    buffer_pool_lib.write_params(context_dict)