import sqlite3
import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QChartView, QBarCategoryAxis
from PyQt5.QtGui import QColor, QBrush, QFont


class Statistics:

    def __init__(self, dashboard_window):
        self.dashboard_window = dashboard_window
        self.results = None
        self.add_chart()

    def add_chart(self):
        data_set = self.get_chart_data()

        set0 = QBarSet("Left Eye")
        set1 = QBarSet("Right Eye")

        set0.setColor(QColor(4, 191, 191))
        set1.setColor(QColor(242,109,109))

        set0.append(data_set[0])
        set1.append(data_set[1])

        series = QBarSeries()
        series.append(set0)
        series.append(set1)

        chart = QChart()
        chart.addSeries(series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        #chart.setBackgroundBrush(QBrush(QColor("transparent")))
        chart.legend().setAlignment(Qt.AlignRight)
        chart.legend().setFont(QFont("Times", weight=QFont.Bold))

        font = QFont("Times", 10)
        font.setWeight(QFont.Bold)
        categories_x = data_set[2]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories_x)
        axis_x.setLabelsFont(font)
        chart.addAxis(axis_x, Qt.AlignBottom)

        categories_y = ["Impaired Vision", "Suboptimal Vision", "Normal Vision", "Enhanced Vision"]
        axis_y = QBarCategoryAxis()
        axis_y.setLabelsFont(QFont("Times", weight=QFont.Bold))
        axis_y.append(categories_y)
        chart.addAxis(axis_y, Qt.AlignLeft)

        self.dashboard_window.chart_view.setChart(chart)

    def get_chart_data(self):
        try:
            connection = sqlite3.connect("accounts.db")
            cursor = connection.cursor()

            try:
                query = f'SELECT Score_left_first, Score_left_second, Score_right_first, Score_right_second, Timestamp FROM Scores WHERE Username_People = {self.dashboard_window.username}'
                cursor.execute(query)
                results = cursor.fetchall()
                self.results = results
                return self.generate_data_range()

            except sqlite3.Error as query_error:
                print("Error executing query:", query_error)

            finally:
                cursor.close()
                connection.close()

        except sqlite3.Error as connection_error:
            print("Error connecting to SQLite database:", connection_error)

    def generate_data_range(self):
        left_eye_data = []
        right_eye_data = []
        timestamp_data = []

        for entry in self.results:
            left_first_row = entry[0]
            left_second_row = entry[1]
            if left_first_row == -1:
                left_first_row = 0
            if left_second_row == -1:
                left_second_row = 0

            left_eye = left_first_row * 2 + left_second_row + 1
            left_eye_data.append(left_eye)

            right_first_row = entry[2]
            right_second_row = entry[3]
            if right_first_row == -1:
                right_first_row = 0
            if right_second_row == -1:
                right_second_row = 0

            right_eye = right_first_row * 2 + right_second_row + 1
            right_eye_data.append(right_eye)

            test = datetime.datetime.fromtimestamp(entry[4]).strftime('%Y-%m-%d %H:%M')
            timestamp_data.append(test)
            print(test)

        return [left_eye_data, right_eye_data, timestamp_data]


