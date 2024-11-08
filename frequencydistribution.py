"""
Created on Fri Nov  8 19:23:20 2024

@author: y_600
@Version: 1.0
@Description: 该脚本用于计算栅格数据的频数分布、百分比和累积百分比。
@Usage: 该脚本需要在 ArcGIS Pro 的 Python 环境中运行，需要提供一个栅格数据和一个目标累积百分比。
@Parameters:
    tif: 输入栅格数据
    tar_accs: 目标累积百分比，以分号分隔
    show_detail: 是否显示详细信息
@Return: 无返回值，直接在控制台输出结果
@Example: python frequency_distribution.py tif.tif 10;20;30 true
@Note: 该脚本仅支持单波段栅格数据，不支持多波段和多维栅格数据。
@Update: 2024-11-08
"""

import os
import arcpy
import numpy as np
from collections import OrderedDict

tif = arcpy.GetParameterAsText(0)
tar_accs = arcpy.GetParameterAsText(1)  
show_detail = arcpy.GetParameter(2) 

tar_accs = tar_accs.split(";")

def searchNearIdx(in_arr, target):
    idx = 0
    active = 1
    while active and idx < len(in_arr):
        if in_arr[idx] > target:
            active = 0
        else:
            idx = idx + 1
    return idx

def showInfo(raster_layer, show_detail=False):
    ndv = raster_layer.noDataValue
    arr_tmp = arcpy.RasterToNumPyArray(raster_layer.catalogPath)
    arr_valid = arr_tmp[(arr_tmp != ndv) & (arr_tmp > -1e38)]
    arr_valid.sort()
    res_count = OrderedDict()
    for i in arr_valid:
        if i not in res_count:
            res_count[i] = 1
        else:
            res_count[i] += 1
    arr_DN = list(res_count.keys())
    arr_Count = list(res_count.values())
    s = float(sum(arr_Count))
    arr_Percent = [(i / s * 100) for i in arr_Count]
    arr_Acc = [arr_Percent[0]]
    for v in arr_Percent[1:]:
        arr_Acc.append(v + arr_Acc[-1])
    if show_detail:
	arcpy.AddMessage("像元值  |  频数  |  频率  |  累积频率")
        infos = ["%5f    %d    %.6f    %.6f" % (vs[0], vs[1], vs[2], vs[3]) for vs in zip(arr_DN, arr_Count, arr_Percent, arr_Acc)]
        arcpy.AddMessage("\n".join(infos))
    for tar in tar_accs:
        arcpy.AddMessage("===============================================")
        tar_idx = searchNearIdx(arr_Acc, float(tar))
	arcpy.AddMessage("目标累积频率 | 实际累积频率 | 对应像元值")
        arcpy.AddMessage("%.6f | %.6f | %.6f" % (float(tar), arr_Acc[tar_idx], arr_DN[tar_idx]))
	arcpy.AddMessage("-------------------------")
	arcpy.AddMessage("目标附近的像元值信息：")
        arcpy.AddMessage("像元值  |  频数  |  频率  |  累积频率")
        num = 5
        for i in range(tar_idx-num//2, tar_idx+num//2):
            if 0 <= i < len(arr_DN):
                arcpy.AddMessage("%5f    %d    %.6f    %.6f" % (arr_DN[i], arr_Count[i], arr_Percent[i], arr_Acc[i]))

raster = arcpy.Raster(tif)
if not raster.bandCount != 1:
    showInfo(raster, show_detail=show_detail)
else:
    arcpy.AddMessage("%s 是多波段数据。该脚本仅支持单波段栅格数据，不支持多波段和多维栅格数据" % tif)
