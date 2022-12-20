import os
import re

import pandas as pd

# excel = pd.read_excel("./23110000100030200002_Численность_постоянного_населения_на_1_января.xlsx")
# csv = pd.read_csv("./Данные csv/Естестественное движение населения.csv")
# lst = [excel, csv]
path="./test_dir/"
list_data = os.listdir(path=path)

for i in list_data:
    a = re.search(r'^[^~$]\w+.+\.xlsx$', i)#re.search(r'[^~$]\w*', i)#(r'[^\w]\w+\.xlsx$', i)
    # print(i)
    if a:
        a = pd.read_excel(f'{path}{i}', sheet_name=i, na_values=['0'])
        print(a)

def foo(**kwargs):
    download_folder = kwargs.get('download_folder', )
    folder_name = kwargs.get('folder_name')

    if not download_folder:
        download_folder = 'Данные скачивания таблиц'
    if not folder_name:
        folder_name = "Данные csv"

    df = pd.read_csv(f'./{folder_name}/Численность населения.csv')

    with pd.ExcelWriter(f"./{download_folder}/Численность населения.xlsx", engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, engine='xlsxwriter', sheet_name='Численность населения'[0:30] if len('Численность населения') > 30 else 'Численность населения')

foo()