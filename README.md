
# dfcompy

## Description

`dfcompy` is a Python package that provides a comprehensive tool for comparing two Pandas DataFrame objects. It can identify rows that are inserted, deleted, or updated between two DataFrames, catering especially to data analysis and data cleaning processes.

## Installation

Install `dfcompy` using pip:

```bash
pip install dfcompy
```

## Usage

```python
import pandas as pd
from dfcompy import DataFrameComparator

# Create example DataFrames
# ... [example DataFrame creation]

# Create a DataFrameComparator instance
comparator = DataFrameComparator(df1, df2, on=['ID'], subset=['Name', 'Age'])

# Detect deleted rows
print("Deleted Rows:")
print(comparator.rows_deleted())

# Detect inserted rows
print("\nInserted Rows:")
print(comparator.rows_inserted())

# Detect updated rows
print("\nUpdated Rows:")
print(comparator.rows_before_update())

# Detect unchanged rows
print("\nUnchanged Rows:")
print(comparator.rows_in_common())
```

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
