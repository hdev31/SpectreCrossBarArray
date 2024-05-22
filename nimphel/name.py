cols = 100
rows = 784
nets_col = [f"COL_{i:03d}" for i in range(cols)]
nets_col_neg = [f"COLN_{i:03d}" for i in range(cols)]

for i in nets_col_neg:
    print('i("/I0/' + i + '") ')