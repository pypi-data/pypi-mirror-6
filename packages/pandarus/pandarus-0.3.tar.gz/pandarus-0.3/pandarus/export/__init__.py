from .json_exporter import json_exporter
from .csv_exporter import csv_exporter

try:
    import cPicle as pickle
except ImportError:
    import pickle


def pickle_exporter(data, filepath, **kwargs):
    with open(filepath, "wb") as f:
        pickle.dump(data, f)
    return filepath
