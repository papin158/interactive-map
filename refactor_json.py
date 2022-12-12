import re

b = []
with open(r"./admin_level_6.geojson", mode='r+', encoding='utf-8') as f:
    a = f.readlines()
    b.append(a[0])
    b.append(a[1])


    for i, j in enumerate(a):
        result = re.search(r'Калининград', j)
        if result:
            b.append(a[i])
            b.append(a[i+1])

    b.append(a[-1])


with open(r"./admin_level_6.geojson", mode='w+', encoding='utf-8') as f:
    for i, sub in enumerate(b):
        f.write(b[i])
