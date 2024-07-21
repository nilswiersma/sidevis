import pickle
import numpy as np

class FileAdapter():
    pass

class PickleFileAdapter(FileAdapter):
    def __init__(self, fname):
        self.fname = fname
        with open(f'{fname}.pkl', 'rb') as f:
            self.TRACES = pickle.load(f)
            for idx, t in enumerate(self.TRACES):
                self.TRACES[idx] = np.concat([t])
    
    def get(self, idx):
        return self.TRACES[idx]

    def raw_to_plot(self, arr):
        line_data = np.empty((2, arr.shape[0]), np.int64)
        line_data[0] = np.arange(arr.shape[0])
        line_data[1] = arr
        return line_data.T