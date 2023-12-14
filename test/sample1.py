import pandas as pd
from dfcompy import DataFrameComparator  # 确保从您的模块中导入 DataFrameComparator

# 创建测试数据
data1 = {
    'ID': [1, 2, 3, 4],
    'Name': ['Alice', 'Bob', 'Charlie', 'David'],
    'Age': [25, 30, 35, 40]
}
df1 = pd.DataFrame(data1)

data2 = {
    'ID': [2, 3, 4, 5],
    'Name': ['Bob', 'Charlie', 'Dave', 'Eve'],
    'Age': [30, 36, 40, 45],
    "NewCol": [1, 312, 1, 41]
}
df2 = pd.DataFrame(data2)

# 创建 DataFrameComparator 实例
comparator = DataFrameComparator(df1, df2, on=['ID'], subset=['Name', 'Age'])

print(df1, '\n', df2)

# 检测被删除的行
print("Deleted Rows:")
print(comparator.rows_deleted)

# 检测被插入的行
print("\nInserted Rows:")
print(comparator.rows_inserted)

# 检测被修改的行
print("\nUpdated Rows:")
print(comparator.rows_before_update)

# 检测被修改的行
print("\nAfter Updated Rows:")
print(comparator.rows_after_update)

# 检测未修改的行
print("\nUnchanged Rows:")
print(comparator.rows_in_common)

print(comparator.abstract)
