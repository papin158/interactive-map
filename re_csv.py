import re

b = []

file = r'./data-20140919-structure-20141013.csv'
utf = 'utf-8'
rus = 'cp1251'
enc = rus

with open(file, mode='r+', encoding=enc) as f:
    a = f.readlines()
    b.append(a[0])
    b.append(a[1])


    for i, j in enumerate(a):
        result = re.search(r'Калининград', j)
        if result:
            b.append(a[i])
            b.append(a[i+1])

    b.append(a[-1])


with open(file, mode='w+', encoding=enc) as f:
    for i, sub in enumerate(b):
        f.write(b[i])
