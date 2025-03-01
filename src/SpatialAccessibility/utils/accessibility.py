import pandas as pd
import numpy as np
import time

"""
计算可达性函数

此函数用于计算给定输入数据集的可达性结果。

参数:
InputData_df (DataFrame): 包含需求点和供应点信息的输入数据集。
AccModel (str): 可达性模型，默认为 'Gravity'。可选值有 '2SFCA'、'Gravity' 等。
beta (float): 重力模型参数，默认为 1。
Threshold (int): 2SFCA 模型的阈值，默认为 5000。
Expon (float): 指数模型的参数，默认为 0.8。
print_out (bool): 是否打印输出结果，默认为 True。
use_copy (bool): 是否使用数据的副本进行操作，默认为 True。
time_recorder (bool): 是否记录函数执行时间，默认为 False。

返回:
CurrentAcc (DataFrame): 当前的可达性结果。
summary_Acc (DataFrame): 可达性的描述性统计结果。

该函数首先提取需求点和供应点的数据并进行去重处理，然后根据不同的可达性模型计算距离衰减效应，
接着计算加权的需求人口，再通过一系列矩阵运算得出每个需求点的可达性得分，
最后计算可达性得分的描述性统计信息并返回结果。
"""
def calculate_accessibility(InputData_df, AccModel='Gravity', beta=1, Threshold=5000, Expon=0.8, set_ddof=1, print_out=True, use_copy=True,time_recorder = False):
    """
    计算可达性函数

    参数:
    InputData_df (DataFrame): 输入数据集，包含需求点和供应点的信息
    AccModel (str): 可达性模型，默认为 'Gravity'
    beta (float): 重力模型参数，默认为 1
    Threshold (int): 2SFCA 模型的阈值，默认为 5000
    Expon (float): 指数模型的参数，默认为 0.8
    print_out (bool): 是否打印输出，默认为 True

    返回:
    CurrentAcc (DataFrame): 当前可达性结果
    summary_Acc (DataFrame): 可达性描述性统计结果
    """
    # 记录开始时间
    start_time = time.time()
    # 设置 pandas 显示浮点数的精度，显示 10 位小数
    pd.set_option('display.float_format', lambda x: '%.10f' % x)
    # 设置 numpy 显示精度
    np.set_printoptions(precision=10)

    # 提取需求点数据，去重
    Origin_df = InputData_df[['OriginID', 'O_Demand']].drop_duplicates()
    OriginID = Origin_df['OriginID']
    OriginPopu = Origin_df['O_Demand']

    # 提取供应点数据，去重
    Destination_df = InputData_df[['DestinationID', 'D_Supply']].drop_duplicates()
    DestinationID = Destination_df['DestinationID']
    DestinationSupply = Destination_df['D_Supply']

    # 提取 OD 数据
    if use_copy:
        OD_df = InputData_df[['OriginID', 'DestinationID', 'TravelCost']].copy()
        Distance = OD_df['TravelCost']
        ODpotent = InputData_df[['OriginID', 'O_Demand', 'DestinationID', 'TravelCost']].copy()
    else:
        OD_df = InputData_df[['OriginID', 'DestinationID', 'TravelCost']]
        Distance = OD_df['TravelCost']
        # here the ODpotent is a view of the original data frame
        ODpotent = InputData_df[['OriginID', 'O_Demand', 'DestinationID', 'TravelCost']]

    # 计算总供应量
    TotalSupply = DestinationSupply.sum()

    # 计算需求点和供应点的数量
    demandpt = len(Origin_df)
    demand_popu = OriginPopu.sum()
    supplypt = len(Destination_df)
    # 计算平均可达性
    ave_accessibility = TotalSupply / demand_popu

    # 打印输出基本信息
    if print_out:
        print(f'{demandpt} demand locations with total population of {demand_popu}')
        print(f'{supplypt} facilities with total capacity of {round(TotalSupply, 3)}')
        print(f'Average Accessibility Score is {ave_accessibility}')

    # 根据可达性模型计算距离衰减效应 f(dij)
    if AccModel == '2SFCA':
        ODpotent.loc[:, 'fdij'] = np.where(ODpotent['TravelCost'] <= Threshold, 1, 0)
    elif AccModel == 'Gravity':
        if print_out:
            print(f"Gravity method applied! beta is {beta}")
        ODpotent.loc[:, 'fdij'] = ODpotent['TravelCost'] ** (-1 * beta)
    else:
        ODpotent.loc[:, 'fdij'] = np.exp(-1 * ODpotent['TravelCost'] * Expon)

    # 计算距离衰减效应加权的需求人口 D*(f(dij))
    ODpotent.loc[:, 'Dfdkj'] = ODpotent['O_Demand'] * ODpotent['fdij']
    # 计算每个供应点的总距离加权需求人口
    Sum_Dfdki = ODpotent.groupby('DestinationID')['Dfdkj'].sum().reset_index()

    # 合并数据，计算 Fij 矩阵
    ODpotent = ODpotent.merge(Sum_Dfdki, on='DestinationID', suffixes=('', '_sum'))
    ODpotent.loc[:, 'Fij'] = ODpotent['fdij'] / ODpotent['Dfdkj_sum']

    # 按照 'OriginID' 和 'DestinationID' 对 ODpotent 进行排序
    ODpotent = ODpotent.sort_values(by=['OriginID', 'DestinationID'])

    # 提取 Fij 向量和需求人口向量 vec_D
    vec_Fij = ODpotent['Fij'].values
    vec_D = OriginPopu.values

    # 构建 Fij 矩阵，形状为 (demandpt, supplypt)，然后进行转置
    Fij = np.transpose(vec_Fij.reshape((supplypt, demandpt), order='F'))
    # 构建 D 矩阵，形状为 (demandpt, demandpt)
    # D = np.diag(vec_D)

    # 计算平均可达性向量 A
    # A = np.ones((demandpt, 1)) * ave_accessibility
    if print_out:
        print(f"Fij shape: {Fij.shape}")
        # print(f"D shape: {D.shape}")

    # 计算可达性
    CurrentAcc = pd.DataFrame((DestinationSupply.values.T @ Fij.T).T, columns=['CurrentAcc'])

    # 打印当前标准差的摘要
    if print_out:
        print(f"Current Standard deviation: {round(CurrentAcc['CurrentAcc'].std(ddof=set_ddof), 4)}")
        print(f"Current Variance: {round(CurrentAcc['CurrentAcc'].var(ddof=set_ddof), 4)}")

    # 计算描述性统计
    summary_CurrentAcc = CurrentAcc['CurrentAcc'].describe().round(3)

    summary_Acc = pd.DataFrame({
        'Current_Acc': summary_CurrentAcc
    }).T

    # 记录结束时间并计算用时
    end_time = time.time()
    elapsed_time = end_time - start_time

    if print_out:
        print(summary_Acc)
        print(f"\nFunction 'calculate_accessibility' took {elapsed_time:.4f} seconds to execute.")

    return CurrentAcc, summary_Acc


from geopy.distance import geodesic

def calculate_accessibility_fca(Origin_df, Destination_df, OD_df=None, AccModel='Gravity', beta=1, Threshold=5000, Expon=0.8, set_ddof=1, print_out=True, time_recorder=False):
    """
    计算可达性函数（FCA）

    参数:
    Origin_df (DataFrame): 包含需求点信息的输入数据集，包含 'OriginID', 'O_Demand', 'lat', 'lng' 列
    Destination_df (DataFrame): 包含供应点信息的输入数据集，包含 'DestinationID', 'D_Supply', 'lat', 'lng' 列
    OD_df (DataFrame, optional): 包含 OD 数据的输入数据集，包含 'OriginID', 'DestinationID', 'TravelCost' 列。如果未提供，则根据经纬度计算
    AccModel (str): 可达性模型，默认为 'Gravity'
    beta (float): 重力模型参数，默认为 1
    Threshold (int): 2SFCA 模型的阈值，默认为 5000
    Expon (float): 指数模型的参数，默认为 0.8
    print_out (bool): 是否打印输出，默认为 True
    time_recorder (bool): 是否记录函数执行时间，默认为 False

    返回:
    CurrentAcc (DataFrame): 当前可达性结果
    summary_Acc (DataFrame): 可达性的描述性统计结果
    """
    # 记录开始时间
    start_time = time.time()

    # 如果没有提供 OD_df，则根据经纬度计算
    if OD_df is None:
        OD_list = []
        for _, origin in Origin_df.iterrows():
            for _, destination in Destination_df.iterrows():
                distance = geodesic((origin['lat'], origin['lng']), (destination['lat'], destination['lng'])).meters
                OD_list.append([origin['OriginID'], destination['DestinationID'], distance])
        OD_df = pd.DataFrame(OD_list, columns=['OriginID', 'DestinationID', 'TravelCost'])

    # 提取需求点和供应点数据
    OriginID = Origin_df['OriginID']
    OriginPopu = Origin_df['O_Demand']
    DestinationID = Destination_df['DestinationID']
    DestinationSupply = Destination_df['D_Supply']

    # 计算总供应量
    TotalSupply = DestinationSupply.sum()

    # 计算需求点和供应点的数量
    demandpt = len(Origin_df)
    demand_popu = OriginPopu.sum()
    supplypt = len(Destination_df)
    # 计算平均可达性
    ave_accessibility = TotalSupply / demand_popu

    # 打印输出基本信息
    if print_out:
        print(f'{demandpt} demand locations with total population of {demand_popu}')
        print(f'{supplypt} facilities with total capacity of {round(TotalSupply, 3)}')
        print(f'Average Accessibility Score is {ave_accessibility}')

    # 根据可达性模型计算距离衰减效应 f(dij)
    if AccModel == '2SFCA':
        OD_df.loc[:, 'fdij'] = np.where(OD_df['TravelCost'] <= Threshold, 1, 0)
    elif AccModel == 'Gravity':
        if print_out:
            print(f"Gravity method applied! beta is {beta}")
        OD_df.loc[:, 'fdij'] = OD_df['TravelCost'] ** (-1 * beta)
    else:
        OD_df.loc[:, 'fdij'] = np.exp(-1 * OD_df['TravelCost'] * Expon)

    # 计算距离衰减效应加权的需求人口 D*(f(dij))
    OD_df.loc[:, 'Dfdkj'] = OD_df['O_Demand'] * OD_df['fdij']
    # 计算每个供应点的总距离加权需求人口
    Sum_Dfdki = OD_df.groupby('DestinationID')['Dfdkj'].sum().reset_index()

    # 合并数据，计算 Fij 矩阵
    OD_df = OD_df.merge(Sum_Dfdki, on='DestinationID', suffixes=('', '_sum'))
    OD_df.loc[:, 'Fij'] = OD_df['fdij'] / OD_df['Dfdkj_sum']

    # 按照 'OriginID' 和 'DestinationID' 对 OD_df 进行排序
    OD_df = OD_df.sort_values(by=['OriginID', 'DestinationID'])

    # 提取 Fij 向量和需求人口向量 vec_D
    vec_Fij = OD_df['Fij'].values
    vec_D = OriginPopu.values

    # 构建 Fij 矩阵，形状为 (demandpt, supplypt)，然后进行转置
    Fij = np.transpose(vec_Fij.reshape((supplypt, demandpt), order='F'))

    # 计算可达性
    CurrentAcc = pd.DataFrame((DestinationSupply.values.T @ Fij.T).T, columns=['CurrentAcc'])

    # 打印当前标准差的摘要
    if print_out:
        print(f"Current Standard deviation: {round(CurrentAcc['CurrentAcc'].std(ddof=set_ddof), 4)}")
        print(f"Current Variance: {round(CurrentAcc['CurrentAcc'].var(ddof=set_ddof), 4)}")

    # 计算描述性统计
    summary_CurrentAcc = CurrentAcc['CurrentAcc'].describe().round(3)

    summary_Acc = pd.DataFrame({
        'Current_Acc': summary_CurrentAcc
    }).T

    # 记录结束时间并计算用时
    end_time = time.time()
    elapsed_time = end_time - start_time

    if print_out:
        print(summary_Acc)
        print(f"\nFunction 'calculate_accessibility_fca' took {elapsed_time:.4f} seconds to execute.")

    return CurrentAcc, summary_Acc