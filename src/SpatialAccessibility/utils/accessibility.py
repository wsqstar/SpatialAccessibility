import pandas as pd
import numpy as np

def calculate_accessibility(InputData_df, AccModel='Gravity', beta=1, Threshold=5000, Expon=0.8, print_out=True):
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
    OD_df = InputData_df[['OriginID', 'DestinationID', 'DestinationID', 'TravelCost']].copy()
    Distance = OD_df['TravelCost']
    ODpotent = InputData_df[['OriginID', 'O_Demand', 'DestinationID', 'TravelCost']].copy()

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
        ODpotent['fdij'] = np.where(ODpotent['TravelCost'] <= Threshold, 1, 0)
    elif AccModel == 'Gravity':
        if print_out:
            print(f"Gravity method applied! beta is {beta}")
        ODpotent['fdij'] = ODpotent['TravelCost'] ** (-1 * beta)
    else:
        ODpotent['fdij'] = np.exp(-1 * ODpotent['TravelCost'] * Expon)

    # 计算距离衰减效应加权的需求人口 D*(f(dij))
    ODpotent['Dfdkj'] = ODpotent['O_Demand'] * ODpotent['fdij']
    # 计算每个供应点的总距离加权需求人口
    Sum_Dfdki = ODpotent.groupby('DestinationID')['Dfdkj'].sum().reset_index()

    # 合并数据，计算 Fij 矩阵
    ODpotent = ODpotent.merge(Sum_Dfdki, on='DestinationID', suffixes=('', '_sum'))
    ODpotent['Fij'] = ODpotent['fdij'] / ODpotent['Dfdkj_sum']

    # 按照 'OriginID' 和 'DestinationID' 对 ODpotent 进行排序
    ODpotent = ODpotent.sort_values(by=['OriginID', 'DestinationID'])

    # 提取 Fij 向量和需求人口向量 vec_D
    vec_Fij = ODpotent['Fij'].values
    vec_D = OriginPopu.values

    # 构建 Fij 矩阵，形状为 (demandpt, supplypt)，然后进行转置
    Fij = np.transpose(vec_Fij.reshape((supplypt, demandpt), order='F'))
    # 构建 D 矩阵，形状为 (demandpt, demandpt)
    D = np.diag(vec_D)

    # 计算平均可达性向量 A
    A = np.ones((demandpt, 1)) * ave_accessibility
    if print_out:
        print(f"Fij shape: {Fij.shape}")
        print(f"D shape: {D.shape}")

    # 计算优化前的可达性
    CurrentAcc = pd.DataFrame((DestinationSupply.values.T @ Fij.T).T, columns=['CurrentAcc'])

    # 打印当前标准差的摘要
    if print_out:
        print(f"Current Standard deviation: {round(CurrentAcc['CurrentAcc'].std(), 3)}")

    # 计算描述性统计
    summary_CurrentAcc = CurrentAcc['CurrentAcc'].describe().round(3)

    summary_Acc = pd.DataFrame({
        'Current_Acc': summary_CurrentAcc
    }).T

    if print_out:
        print(summary_Acc)

    return CurrentAcc, summary_Acc