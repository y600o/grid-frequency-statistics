"""
Created on Fri Nov  8 19:23:20 2024

@Version: v2.0
@Description: 该脚本用于计算栅格数据的频数分布、百分比和累积百分比。
@Usage: 该脚本需要在 ArcGIS Pro 的 Python 环境中运行，需要提供一个栅格数据和一个目标累积百分比。
@Parameters:
    tif: 输入栅格数据
    tar_accs: 目标累积百分比，以分号分隔
    show_detail: 是否显示详细信息
@Return: 无返回值，直接在控制台输出结果
@Example: python frequency_distribution.py tif.tif 10;20;30 true
@Note: 该脚本仅支持单波段栅格数据，不支持多波段和多维栅格数据。
@Update: 2024-11-09
@Author: y_600
"""

import os
import arcpy
import numpy as np
from bisect import bisect_left

def get_parameters():
    tif = arcpy.GetParameterAsText(0)
    tar_accs = arcpy.GetParameterAsText(1)
    show_detail = arcpy.GetParameter(2)
    tar_accs = [float(tar) for tar in tar_accs.split(";")]
    return tif, tar_accs, show_detail

def search_near_idx(in_arr, target):
    idx = bisect_left(in_arr, target)
    return idx if idx < len(in_arr) else len(in_arr) - 1

def process_raster(raster_layer, tar_accs, show_detail=False):
    ndv = raster_layer.noDataValue
    arr_tmp = arcpy.RasterToNumPyArray(raster_layer.catalogPath)
    arr_valid = arr_tmp[(arr_tmp != ndv) & (arr_tmp > -1e38)]
    arr_valid.sort()
    
    unique, counts = np.unique(arr_valid, return_counts=True)
    s = float(counts.sum())
    arr_percent = (counts / s * 100).tolist()
    arr_acc = np.cumsum(arr_percent).tolist()
    
    if show_detail:
        display_details(unique, counts, arr_percent, arr_acc)
    
    display_target_info(unique, counts, arr_percent, arr_acc, tar_accs)

def display_details(unique, counts, arr_percent, arr_acc):
    arcpy.AddMessage("像元值  |  频数  |  频率  |  累积频率")
    infos = ["%5f    %d    %.6f    %.6f" % (vs[0], vs[1], vs[2], vs[3]) for vs in zip(unique, counts, arr_percent, arr_acc)]
    arcpy.AddMessage("\n".join(infos))

def display_target_info(unique, counts, arr_percent, arr_acc, tar_accs):
    for tar in tar_accs:
        arcpy.AddMessage("===============================================")
        tar_idx = search_near_idx(arr_acc, tar)
        arcpy.AddMessage("目标累积频率 | 实际累积频率 | 对应像元值")
        arcpy.AddMessage("%.6f | %.6f | %.6f" % (tar, arr_acc[tar_idx], unique[tar_idx]))
        arcpy.AddMessage("-------------------------")
        arcpy.AddMessage("目标附近的像元值信息：")
        arcpy.AddMessage("像元值  |  频数  |  频率  |  累积频率")
        num = 5
        for i in range(max(0, tar_idx-num//2), min(len(unique), tar_idx+num//2)):
            arcpy.AddMessage("%5f    %d    %.6f    %.6f" % (unique[i], counts[i], arr_percent[i], arr_acc[i]))

def main():
    tif, tar_accs, show_detail = get_parameters()
    raster = arcpy.Raster(tif)
    if raster.bandCount == 1:
        process_raster(raster, tar_accs, show_detail=show_detail)
    else:
        arcpy.AddMessage("%s 是多波段数据。该脚本仅支持单波段栅格数据，不支持多波段和多维栅格数据" % tif)

if __name__ == "__main__":
    main()
