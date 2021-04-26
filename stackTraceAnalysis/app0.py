from random import seed
from random import randrange
from csv import reader
from math import exp
def main():
    seed(1)
    filename = 'pima-indians-diabetes.csv'
    load_csv_dataset = list()
    with open(filename, 'r') as load_csv_file:
        load_csv_csv_reader = reader(load_csv_file)
        for load_csv_row in load_csv_csv_reader:
            if (not load_csv_row):
                continue
            load_csv_dataset.append(load_csv_row)
