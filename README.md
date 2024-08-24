# SpatialAccessibility Lib
This is a library for spatial accessibility analysis in Python. 

## Installation
To install the library, you can use pip:

```
pip install -i https://test.pypi.org/simple/ SpatialAccessibility==0.0.1

```
or if you ara using Colab:

```
!pip install hatchling
!pip install git+https://github.com/wsqstar/SpatialAccessibility.git

```

## Usage
To use the library, you need to have a od matrix of the study area. You can then use the following code to calculate the spatial accessibility:
```python
from SpatialAccessibility import calculate_accessibility
# @title 示例调用
import pandas as pd
Data_df = pd.read_csv("datasets/Data.csv")

Data_df.rename(columns={'O_Popu': 'O_Demand'}, inplace=True)
Current_Accessibility, summary_accessibility = calculate_accessibility(Data_df,print_out=False)

# Load the dataframe
```