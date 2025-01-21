import pandas as pd
import os
import matplotlib.pyplot as plt


def read_accessibility_file(file_path):
    """
    函数 1：读取可达性计算文件
    :param file_path: 文件的路径
    :return: 读取的 DataFrame
    """
    df = pd.read_csv(file_path)
    return df


import pandas as pd


import pandas as pd

def calculate_df_parameters(df, specified_ids=None):
    results = {}
    
    # 计算整体参数
    results['all'] = {
        'mean': df['accessibility'].mean(),
        'variance': df['accessibility'].var(),
        'quartiles': df['accessibility'].quantile([0.25, 0.5, 0.75])
    }
    
    # 处理 specified_ids
    if specified_ids is not None:
        # === 改进点1：明确处理空列表 ===
        is_empty_input = (len(specified_ids) == 0)
        if is_empty_input:
            results['specified_status'] = 'empty_input'
            return results  # 提前返回空输入状态
        
        # === 改进点2：处理 NaN 值 ===
        # 方案选择1：抛出异常
        if any(pd.isna(x) for x in specified_ids):
            raise ValueError("specified_ids 包含 NaN 值")
        
        # 方案选择2：自动过滤 NaN（根据需求选择）
        clean_ids = [x for x in specified_ids if pd.notna(x)]
        unique_ids = list(set(clean_ids))
        
        # 过滤 DataFrame
        valid_ids = df['id'].dropna()
        df_specific = df[valid_ids.isin(unique_ids)]
        
        # 记录状态
        if df_specific.empty:
            results['specified_status'] = 'no_matching_data'
        else:
            results['specific'] = {
                'mean': df_specific['accessibility'].mean(),
                'variance': df_specific['accessibility'].var(),
                'quartiles': df_specific['accessibility'].quantile([0.25, 0.5, 0.75])
            }
            results['specified_status'] = 'success'
    
    return results

def batch_read_accessibility_results(folder_paths):
    """
    函数 3：批量读取不同文件夹内的可达性计算结果
    :param folder_paths: 包含可达性计算结果的文件夹路径列表
    :return: 存储读取结果的列表
    """
    results = []
    for folder_path in folder_paths:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    df = read_accessibility_file(file_path)
                    results.append(df)
    return results


def compare_accessibility_results(df_list):
    """
    函数 4：比较可达性结果
    :param df_list: 存储多个 DataFrame 的列表
    :return: 比较结果（这里假设比较不同 DataFrame 的平均值）
    """
    comparison_results = []
    for df in df_list:
        mean_accessibility = calculate_df_parameters(df)
        comparison_results.append(mean_accessibility)
    return comparison_results


def generate_text_report(comparison_results):
    """
    函数 5：生成文字汇报
    :param comparison_results: 比较结果列表
    :return: 文字汇报字符串
    """
    report = "可达性优化前后比较报告：\n"
    for i, result in enumerate(comparison_results):
        report += f"结果 {i + 1}: 平均值为 {result}\n"
    return report


def generate_image_report(comparison_results):
    """生成图像汇报（修正版）"""
    # 从比较结果中提取平均值
    values = [res['all']['mean'] for res in comparison_results]
    plt.figure()
    plt.bar(range(len(values)), values)
    plt.xlabel('结果编号')
    plt.ylabel('可达性平均值')
    plt.title('可达性优化前后比较')
    plt.show()


# 示例使用
if __name__ == "__main__":
    folder_paths = ['path/to/folder1', 'path/to/folder2']
    df_list = batch_read_accessibility_results(folder_paths)
    comparison_results = compare_accessibility_results(df_list)
    text_report = generate_text_report(comparison_results)
    print(text_report)
    generate_image_report(comparison_results)