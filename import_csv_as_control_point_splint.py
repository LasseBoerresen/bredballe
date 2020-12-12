# Author-Autodesk Inc.
# Description-Import spline from csv file



import os
import sys


sys.path.append('C:/Users/lb/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Python/defs')


import adsk.core, adsk.fusion, traceback
import io


def run(context):
    try_run()


def try_run():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        _run(app, ui)
    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def _run(app, ui):
    design, title = get_components(app, ui)
    dlg = open_file(ui)
    add_spline_from_file(design, dlg.filename, title, ui)


def get_components(app, ui):
    # Get all components in the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    title = 'Import Spline csv'
    if not design:
        ui.messageBox('No active Fusion design', title)
        raise Exception('no active fusion design')
    return design, title


def open_file(ui):
    dlg = ui.createFileDialog()
    dlg.title = 'Open CSV File'
    dlg.filter = 'Comma Separated Values (*.csv);;All Files (*.*)'
    if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
        raise Exception('file dialog not ok')
    return dlg


def add_spline_from_file(design, filename, title, ui):
    points = adsk.core.ObjectCollection.create()
    for line in read_lines(filename):
        points.add(convert_line_to_point(line))
    if points.count > 0:
        add_spline(design, points)
    else:
        ui.messageBox('No valid points', title)


def add_spline(design, points):
    root = design.rootComponent
    sketch = root.sketches.add(root.xYConstructionPlane)
    sketch.sketchCurves.sketchFittedSplines.addByNurbsCurve(points)

def read_lines(filename):
    with io.open(filename, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    return lines


def convert_line_to_point(line):
    data = []
    pntStrArr = line.split(',')
    for pntStr in pntStrArr:
        try:
            data.append(float(pntStr))
        except Exception as e:
            break
    if len(data) >= 3:
        point = adsk.core.Point3D.create(data[0], data[1], data[2])
    return point


def main():
    pass


if __name__ == '__main__':
    main()