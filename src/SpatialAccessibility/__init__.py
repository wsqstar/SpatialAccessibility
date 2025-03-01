# 导入 utils 子包中的 Photo 类
from .utils.accessibility import calculate_accessibility,calculate_accessibility_fca
from .utils.compare import read_accessibility_file, calculate_df_parameters, batch_read_accessibility_results, compare_accessibility_results, generate_text_report, generate_image_report

__version__ = '0.0.1'
__author__ = 'Shiqi Wang'
