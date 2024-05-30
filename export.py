import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows


def export(data_set, filename):
    data = {
        'Timestamp': data_set[2],
        'Left Eye': data_set[0],
        'Right Eye': data_set[1],
        'Vision Status Left Eye': data_set[3],
        'Vision Status Right Eye': data_set[4]
    }

    df = pd.DataFrame(data)

    wb = Workbook()
    ws = wb.active
    ws.title = "Vision Assessment Data"

    for row in dataframe_to_rows(df, index=False, header=True):
        ws.append(row)

    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    chart = BarChart()

    data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=len(df) + 1)
    categories = Reference(ws, min_col=1, min_row=2, max_row=len(df) + 1)

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)

    chart.title = "Vision Assessment"
    chart.y_axis.title = "Vision Level"
    chart.x_axis.title = "Timestamp"

    chart.y_axis.scaling.min = 0
    chart.y_axis.scaling.max = 4
    chart.y_axis.majorUnit = 1
    chart.y_axis.number_format = '0'

    ws.add_chart(chart, "F1")
    output_path = filename
    wb.save(output_path)

