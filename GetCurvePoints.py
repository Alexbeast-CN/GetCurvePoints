import adsk.core, adsk.fusion, adsk.cam, traceback
import csv
import os

def run(context):
    try:
        # 获取应用程序和用户界面
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # 选择目标曲线
        # ui.messageBox('请在视图中选择你的管道曲线。')
        sel = ui.selectEntity('选择曲线', 'SketchCurves,Edges')
        if not sel:
            return
        curve = sel.entity
        
        # 获取曲线所在草图平面
        sketch = curve.parentSketch
        
        # 获取草图平面相对于全局坐标系的变换矩阵
        transform = sketch.transform
        
        # 获取曲线长度
        evaluator = curve.geometry.evaluator
        success, curveLength = evaluator.getLengthAtParameter(0.0, 1.0)
        if not success:
            ui.messageBox('无法获取曲线长度，操作取消。')
            return
        # 设置散点间距（厘米）
        spacing = 3.0
        # 计算点的数量
        num_points = int(curveLength / spacing) + 1
        param_step = 1.0 / (num_points - 1)
        
        # 计算等距点并转换为全局坐标
        points = []
        for i in range(num_points):
            param = param_step * i
            success, point = evaluator.getPointAtParameter(param)
            if success:
                # 将点坐标乘以变换矩阵，得到全局坐标
                success = point.transformBy(transform)  # 将转换结果赋给新的对象
                points.append(point)
        
        # 创建文件对话框
        fileDialog = ui.createFileDialog()
        fileDialog.isMultiSelectEnabled = False
        fileDialog.title = "指定保存位置"
        fileDialog.filter = 'CSV 文件 (*.csv)'
        fileDialog.filterIndex = 0
        dialogResult = fileDialog.showSave()
        
        # 设置缩放比例
        scale = 0.01
        if dialogResult == adsk.core.DialogResults.DialogOK:
            filepath = fileDialog.filename
            
            # 写入CSV文件，指定UTF-8编码
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=' ')  # 设置分隔符为空格
                writer.writerow(['X', 'Y', 'Z'])  # 写入表头
                for i, point in enumerate(points):
                    writer.writerow([point.x*scale, point.y*scale, point.z*scale])
            
            ui.messageBox(f'已成功将 {len(points)} 个点保存到文件：\n{filepath}')
    
    except:
        if ui:
            ui.messageBox('失败:\n{}'.format(traceback.format_exc()))