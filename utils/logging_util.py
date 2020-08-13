# -*- coding: utf-8 -*-
import logging
import sys
from io import BytesIO
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def get_std_logging():
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
        level=logging.INFO
    )
    return logging

class log_tool():
    def __init__(self, bucket=None, load_old=True, log_path='', log_png=''):
        self.step = []
        self.value = []
        self.bucket = bucket
        self.log_path = log_path
        self.log_png = log_png
        if not (bucket is None or log_path == '') and load_old:
            self.load_log()

    def update(self, s, v):
        self.step.append(s)
        self.value.append(v)

    def sample(self, sample_num=100):
        if len(self.step) > sample_num:
            self.x = np.array(self.step)[::len(self.step) // sample_num].tolist()
            self.y = np.array(self.value)[::len(self.step) // sample_num].tolist()
        else:
            self.x = self.step
            self.y = self.value

    def plot(self, sample_num=100, x_label='iter', y_label='loss'):
        self.sample(sample_num=sample_num)
        _, ax = plt.subplots()
        style = 'r*-'
        ax.plot(self.x, self.y, style, label=f'{y_label}_last:{self.y[-1]:.2f}')
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid()
        ax.legend()
        buf = BytesIO()
        plt.savefig(buf, dpi=150)
        try:
            self.bucket.put_object(self.log_png, buf.getvalue())
        except Exception as e:
            print(e)

    def load_log(self):
        try:
            lines = str(self.bucket.get_object(self.log_path).read(), 'utf-8').split('\n')
            for line in lines:
                if not line:
                    continue
                s, v = line.split(' ')
                self.step.append(int(s))
                self.value.append(float(v))
        except Exception as e:
            print(e)

    def save_log(self):
        if not (self.bucket is None or self.log_path == ''):
            fp = BytesIO()
            for idx, s in enumerate(self.step):
                line = f'{s} {self.value[idx]}\n'
                fp.write(line.encode('utf-8'))
            try:
                self.bucket.put_object(self.log_path, fp.getvalue())
            except Exception as e:
                print(e)
