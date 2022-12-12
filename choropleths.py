import asyncio
import colorsys
from typing import Tuple

import pandas as pd
import numpy as np

data_kld = pd.read_csv('./Данные csv/КалининградСтат - Данные - Естест. движение насел.csv')
data_ = pd.read_csv('./январь_2021_г_,_23110000100030200002_Численность_постоянного_населения_на_1_января.csv',
                    encoding='cp1251')

# for k in data_kld:
#     data_kld[k] = [str(i) for i in k]
data_kld = data_kld.astype('str')
# data_kld = data_kld.set_index('Городские округа:')
data_kld_lop = data_kld.copy()
data_kld_lop.pop('Городские округа:')
data_kld_lop = data_kld_lop.astype(np.int64)

d = data_kld_lop.columns.tolist()
# for k in data_kld_lop:
#     print(data_kld[k])
#     #print(data_kld[k])
#        #  print(data_kld[k])
var_name = 'Год'.encode('utf8').decode('utf8')
data_loc = pd.melt(data_kld, id_vars='Городские округа:', var_name=var_name, value_name='Изменения', value_vars=d, )
data_loc.sort_values('Городские округа:')

# data_kld['dynamic_sum'] = data_kld_lop.astype(np.int64).sum(axis=1)
data_kld['dynamic_sum'] = data_kld.copy()._drop_axis(labels='Городские округа:', axis=1).astype(np.int64).sum(axis=1)

data = (data_kld['dynamic_sum'].quantile((0.0, 0.1, 0.3, 0.4, 0.5, 0.6, 0.7, 0.89, 0.98, 1.0))).tolist()

labels = {'Население': True, "Естественное движение населения": False}


def rgb2hsv(rgb):
    """ convert RGB to HSV color space

    :param rgb: np.ndarray
    :return: np.ndarray
    """

    rgb = rgb.astype('float')
    maxv = np.amax(rgb, axis=2)
    maxc = np.argmax(rgb, axis=2)
    minv = np.amin(rgb, axis=2)
    minc = np.argmin(rgb, axis=2)

    hsv = np.zeros(rgb.shape, dtype='float')
    hsv[maxc == minc, 0] = np.zeros(hsv[maxc == minc, 0].shape)
    hsv[maxc == 0, 0] = (((rgb[..., 1] - rgb[..., 2]) * 60.0 / (maxv - minv + np.spacing(1))) % 360.0)[maxc == 0]
    hsv[maxc == 1, 0] = (((rgb[..., 2] - rgb[..., 0]) * 60.0 / (maxv - minv + np.spacing(1))) + 120.0)[maxc == 1]
    hsv[maxc == 2, 0] = (((rgb[..., 0] - rgb[..., 1]) * 60.0 / (maxv - minv + np.spacing(1))) + 240.0)[maxc == 2]
    hsv[maxv == 0, 1] = np.zeros(hsv[maxv == 0, 1].shape)
    hsv[maxv != 0, 1] = (1 - minv / (maxv + np.spacing(1)))[maxv != 0]
    hsv[..., 2] = maxv

    return hsv


def hsv2rgb(hsv):
    """ convert HSV to RGB color space

    :param hsv: np.ndarray
    :return: np.ndarray
    """

    hi = np.floor(hsv[..., 0] / 60.0) % 6
    hi = hi.astype('uint8')
    v = hsv[..., 2].astype('float')
    f = (hsv[..., 0] / 60.0) - np.floor(hsv[..., 0] / 60.0)
    p = v * (1.0 - hsv[..., 1])
    q = v * (1.0 - (f * hsv[..., 1]))
    t = v * (1.0 - ((1.0 - f) * hsv[..., 1]))

    rgb = np.zeros(hsv.shape)
    rgb[hi == 0, :] = np.dstack((v, t, p))[hi == 0, :]
    rgb[hi == 1, :] = np.dstack((q, v, p))[hi == 1, :]
    rgb[hi == 2, :] = np.dstack((p, v, t))[hi == 2, :]
    rgb[hi == 3, :] = np.dstack((p, q, v))[hi == 3, :]
    rgb[hi == 4, :] = np.dstack((t, p, v))[hi == 4, :]
    rgb[hi == 5, :] = np.dstack((v, p, q))[hi == 5, :]

    return rgb


data_kld = list(data_kld['Городские округа:'].unique())
data_len = len(data_kld)

max_columns = 3
no = 0
n = round(data_len / max_columns)+1

if data_len < max_columns:
    raise ValueError("Количество колонок превышает количество значений")

a = {0: 1, 1: 2, 2: 3, }
for an in range(max_columns):
    if a[an]:

        if n <= data_len:
            for i in range(no, n):
                print(data_kld[i][0:4])
        else:
            print(data_kld[n][0:4])

        no = n
        n += round(data_len / max_columns)




