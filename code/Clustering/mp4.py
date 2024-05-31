import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


if __name__ == '__main__':
    case2 = pd.read_excel(io='./2.xlsx')
    x=case2['X']
    y=case2['Y']
    z=case2['Z']
    fig0 = px.scatter_3d(case2,x="X",y="Y",z="Z",color="Group designtor",size_max=0.1)
    fig0.update_layout(title={'text': "初始数据"})
    fig0.show()
    fig0.write_image(f'./初始数据.png')
    #pio.write_image(fig0, f'./初始数据.png')
    
    x_array = np.array(x)
    y_array = np.array(y)
    z_array = np.array(z)
    if True:
        max_x = max(x_array)
        min_x = min(x_array)
        x_array = (x_array - min_x) / (max_x - min_x)
        max_y = max(y_array)
        min_y = min(y_array)
        y_array = (y_array - min_y) / (max_y - min_y)
        max_z = max(z_array)
        min_z = min(z_array)
        z_array = (z_array - min_z) / (max_z - min_z)
    data = np.stack((x_array, y_array, z_array), axis=1)
    init_data = data

    # 初始化聚类中心
    kmeans = KMeans(n_clusters=6)
    print(kmeans.max_iter)
    k = 6
    centroids = data[np.random.choice(data.shape[0], k, replace=False)]
    # 迭代聚类
    for i in range(6):
        # 计算每个数据点到聚类中心的距离
        distances = np.sqrt(((data - centroids[:, np.newaxis]) ** 2).sum(axis=2))
        # 将每个数据点分配到最近的聚类中心
        labels = np.argmin(distances, axis=0)
        # 更新聚类中心
        for j in range(k):
            centroids[j] = np.mean(data[labels == j], axis=0)
        case2['type'] = labels
        fig = px.scatter_3d(case2, x="X", y="Y", z="Z", color="type", size_max=0.1)
        fig.update_layout(title={'text': f"迭代数据{i}"})
        fig.show()
        #fig.write_image(f'./迭代数据{i}.png')
