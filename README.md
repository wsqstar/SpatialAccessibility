# [SpatialAccessibility Lib](https://github.com/wsqstar/SpatialAccessibility)

![PyPI - Version](https://img.shields.io/pypi/v/SpatialAccessibility)

This is a library for spatial accessibility analysis in Python， hosted on https://github.com/wsqstar/SpatialAccessibility .
> Inspried by the work of Prof.Fahui Wang and Dr.Lingbo Liu, DOI: 10.1201/9781003292302-14

## Installation
To install the library, you can use pip:

```
pip install SpatialAccessibility

```
or if you ara using Colab:

```
!pip install hatchling==1.26.3 build twine
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