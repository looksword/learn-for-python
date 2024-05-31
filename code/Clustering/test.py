import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # 空间三维画图
from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture
from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix
from multiprocessing import Pool
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score


if __name__ == '__main__':
    case2 = pd.read_excel(io='./2.xlsx')
    #print(case2.dtypes)
    #print(case2['X'])
    x=case2['X']
    y=case2['Y']
    z=case2['Z']
    #绘图
    fig0 = px.scatter_3d(case2,x="X",y="Y",z="Z",color="Group designtor",size_max=0.1)
    fig0.update_layout(title={'text': "初始数据"})
    fig0.show()

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
    
    #case2_one = pd.DataFrame(data, columns=['X','Y','Z'])
    #case2_one["Group designtor"] = case2["Group designtor"]
    #fig0_0 = px.scatter_3d(case2_one,x="X",y="Y",z="Z",color="Group designtor",size_max=0.1)
    #fig0_0.update_layout(title={'text': "初始数据(归一化)"})
    #fig0_0.show()
    
    
    #print(data)
    #fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
    #ax1.hist(x_array, bins=30, density=True, alpha=0.5)
    #ax2.hist(y_array, bins=30, density=True, alpha=0.5)
    #ax3.hist(z_array, bins=30, density=True, alpha=0.5)
    #plt.tight_layout()
    #plt.show()

    #c = DBSCAN(eps=0.1, min_samples=1).fit(data)
    #print(len(c.labels_))
    #case2['type'] = c.labels_
    #labels = c.labels_
    #n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    #n_noise_ = list(labels).count(-1)
    #print("n_clusters_:",n_clusters_)
    #print("n_noise_:",n_noise_)
    
    kmeans = KMeans(n_clusters=6)
    kmeans.fit(data)
    cluster_centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    case2['type'] = kmeans.labels_
    
    #agg_cluster = AgglomerativeClustering(n_clusters=6, linkage='ward')
    #agg_cluster.fit(data)
    #labels = agg_cluster.labels_
    #case2['type'] = agg_cluster.labels_
    
    #gmm = GaussianMixture(n_components=6)
    #gmm.fit(data)
    #labels = gmm.predict(data)
    #case2['type'] = labels
    
    #spectral = SpectralClustering(n_clusters=6)
    #spectral.fit(data)
    #labels = spectral.labels_
    #case2['type'] = spectral.labels_
    
    fig1 = px.scatter_3d(case2,x="X",y="Y",z="Z",color="type",size_max=0.1)
    fig1.update_layout(title={'text': "K-Means(clusters=6)"})
    fig1.show()
    
    #case2_one["type"] = kmeans.labels_
    #fig1_0 = px.scatter_3d(case2_one,x="X",y="Y",z="Z",color="type",size_max=0.1)
    #fig1_0.update_layout(title={'text': "K-Means(clusters=6)(归一化)"})
    #fig1_0.show()
    
    if True:
        # 计算轮廓系数:衡量每个数据点与其分配簇的相似度和与其他簇的差异度；越接近1越好
        silhouette_coeff = silhouette_score(data, labels)
        # 计算戴维斯-鲍尔丁指数：衡量簇之间的分离度和紧凑度；越小越好
        davies_bouldin = davies_bouldin_score(data, labels)
        # 计算卡莱斯基-哈拉巴兹指数：衡量簇内差异和簇间差异的比率；越大越好
        calinski_harabasz = calinski_harabasz_score(data, labels)
        print("kmeans 6 聚类分析:")
        print("轮廓系数", silhouette_coeff)
        print("Davies-Bouldin 指数", davies_bouldin)
        print("Calinski-Harabasz 指数", calinski_harabasz)
        
        silhouette_coeff_old = silhouette_score(data, case2['Group designtor'])
        davies_bouldin_old = davies_bouldin_score(data, case2['Group designtor'])
        calinski_harabasz_old = calinski_harabasz_score(data, case2['Group designtor'])
        print("初始标签 聚类分析:")
        print("轮廓系数", silhouette_coeff_old)
        print("Davies-Bouldin 指数", davies_bouldin_old)
        print("Calinski-Harabasz 指数", calinski_harabasz_old)

    if False:
        score2 = pd.DataFrame(np.array([['kmeans 6','轮廓系数'],['kmeans 6','Davies-Bouldin 指数'],['kmeans 6','Calinski-Harabasz 指数'],['初始标签','轮廓系数'],['初始标签','Davies-Bouldin 指数'],['初始标签','Calinski-Harabasz 指数']]), columns=['批次','指数'])
        score2['数值'] = [silhouette_coeff,davies_bouldin,calinski_harabasz,silhouette_coeff_old,davies_bouldin_old,calinski_harabasz_old]
        
        centers2 = pd.DataFrame(cluster_centers, columns=['X','Y','Z'])
        old_centers = []
        for i in range(6):
            old_center = []
            old_center.append(cluster_centers[i][0] * (max_x - min_x) + min_x)
            old_center.append(cluster_centers[i][1] * (max_y - min_y) + min_y)
            old_center.append(cluster_centers[i][2] * (max_z - min_z) + min_z)
            old_centers.append(old_center)
        centers2[['old X','old Y','old Z']] = pd.DataFrame(old_centers, index=centers2.index)
        centers2['type'] = list(range(6))
        
        center_dist = []
        for i in range(len(data)):
            new_dist = np.linalg.norm(data[i] - cluster_centers[labels[i]])
            center_dist.append(new_dist)
        dist2 = pd.DataFrame(data, columns=['聚类 X','聚类 Y','聚类 Z'])
        dist2['distance'] = center_dist
        
        writer = pd.ExcelWriter("result(kmeans 6 归一化).xlsx")
        case2.to_excel(writer, sheet_name='聚类结果', index=False)
        dist2.to_excel(writer, sheet_name='聚类中心距离', index = False)
        centers2.to_excel(writer, sheet_name='聚类中心位置', index = False)
        score2.to_excel(writer, sheet_name='评估指标', index=False)
        writer.save()
        writer.close()
