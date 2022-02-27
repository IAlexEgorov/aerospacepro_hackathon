from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd
import numpy as np
import networkx as nx


def flatten(t):
    """
    :param t: Принимает список с вложенным списком пример: [[1, 2, 3]]
    :return: Возвращает список пример: [1,2,3]
    """
    return [item for sublist in t for item in sublist]


def gettextwithsearch(list_a):
    """
    :param list_a: Список из описании компонента
    :return: Возвращает строку для вывода на интерфейс
    """
    return str(f'Компонента 2: {list_a[2]}\nДатчик 1: {list_a[3]}\n'
               f'Датчик 2: {list_a[4]}\nДатчик 3: {list_a[5]}\n'
               f'Датчик 4: {list_a[6]}\nДатчик 5: {list_a[7]}\n'
               f'Датчик 6: {list_a[8]}\nДатчик 7: {list_a[9]}\n')


def drop_extra(x):
    """
    :param x: Получает строку
    :return: Возвращает список числовых значении
    """
    x = list(map(int, x.split('-')))
    if len(x) == 1 or len(x) != len(set(x)) or sorted(x) != x:
        return False
    return x


def help():
    """
    :return: Открывает браузер для перехода на страницу справки
    """
    import webbrowser
    url = 'https://docs.google.com/document/d/121rUNowQXIKmam13V0rwFUcevYB_RCznF3P0Tsc1bmY/edit?usp=sharing'
    webbrowser.open_new(url)


class PlotCanvas(FigureCanvas):
    """
    Класс для рисования в интерфейсе с помощью библиотеки Matplotlib.
    Графы будут нарисованы здесь.
    """
    def __init__(self, parent=None, width=500, height=500, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.set_facecolor("none")

        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.graph = nx.Graph()
        self.graph_usels = 0

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.setStyleSheet("background-color: lightblue;")


    def plot_all(self, graph_usels):
        """

        :param graph_usels: Список всех компонент для рисования узлов
        :return: Рисует все узлы и связи между ними при открытии файлов
        """
        self.graph = nx.Graph()
        self.graph_usels = graph_usels
        graph_values = []  # список всех узлов графа
        for unit in graph_usels[:]:
            for i in range(len(unit)):
                if unit[i] not in graph_values:
                    graph_values.append(unit[i])
                    self.graph.add_node(unit[i])

                if i == 1:
                    self.graph.add_edge(unit[1], unit[0], color='black')
                elif i == 2:
                    self.graph.add_edge(unit[2], unit[1], color='black')
                elif i == 3:
                    self.graph.add_edge(unit[3], unit[2], color='black')
        nx.draw(self.graph, node_color='red', with_labels=True, ax=self.axes)

    def select_nodes(self, points):
        """

        :param points: узлы предков
        :return: Выделяет узлы предков point
        """
        self.axes.clear()
        color_map = []
        node_size_map = []
        for node in self.graph:
            if node in points:
                color_map.append('green')
                node_size_map.append(1000)
            else:
                color_map.append('red')
                node_size_map.append(100)
        edges = self.graph.edges()
        if len(points) > 1:
            for i in range(len(points)-1):
                self.graph[points[i]][points[i+1]]['color'] = 'g'
        # edge_colors = [self.graph[u][v]['color'] for u, v in edges]
        nx.draw(self.graph, node_color=color_map, node_size=node_size_map,
                ax=self.axes, with_labels=True)

        self.draw_idle()


class MPLWidget(QWidget):
    """
    Главный класс интерфейса
    """
    def __init__(self):
        super().__init__()
        self.setGeometry(0,0, 1000, 800)
        self.setStyleSheet("background-color: lightblue;")
        self.setWindowTitle("ITAlpha Case3")
        self.setWindowIcon(QIcon("src/icon.png"))



        self.canvas = PlotCanvas()

        layoutmain = QHBoxLayout(self)
        layout1 = QVBoxLayout()
        toolbar = NavigationToolbar(self.canvas, self)
        layout1.addWidget(toolbar)
        layout1.addWidget(self.canvas)
        layout2 = QVBoxLayout()

        self.buttonopenfiles = QPushButton("")
        self.buttonopenfiles.setIcon(QIcon("src/open.png"))
        self.buttonopenfiles.setIconSize(QSize(24, 24))
        self.buttonopenfiles.setToolTip("Открыть файлы")
        self.buttonopenfiles.clicked.connect(self.openfiles)

        self.labelnumbernodes = QLabel("Количество компонентов: 0")

        self.labelinfo = QLabel("")
        self.labelinfo.hide()

        self.lineeditnode = QLineEdit()
        self.lineeditnode.setPlaceholderText("Введите номер компонента")

        self.buttonstart = QPushButton("")
        self.buttonstart.setIcon(QIcon("src/search.png"))
        self.buttonstart.setIconSize(QSize(24, 24))
        self.buttonstart.setToolTip("Найти компоненту")
        self.buttonstart.clicked.connect(self.searchNode)

        self.buttonhelp = QPushButton("Справка")
        self.buttonhelp.clicked.connect(help)

        layout2.addWidget(self.buttonopenfiles)
        layout2.addWidget(self.labelnumbernodes)
        layout2.addWidget(self.labelinfo)
        layout2.addWidget(self.lineeditnode)
        layout2.addWidget(self.buttonstart)
        layout2.addWidget(self.buttonhelp)
        layoutmain.addLayout(layout1)
        layoutmain.addLayout(layout2)
        self.files_csv = []
        self.nodesnumber = 0
        self.df_original = None



    def openfiles(self):
        self.files_csv = QFileDialog.getOpenFileNames(self, 'Открыть файлы', './', "CSV (*.csv)")[0]

        cols = ['comp_1', 'tree', 'extra', '3', '4', '5', '6', '7', '8', '9']

        df = pd.read_csv(self.files_csv[0], header=None, names=cols)
        for i in range(1, 10):
            new = pd.read_csv(self.files_csv[i], header=None, names=cols)
            df = pd.concat([df, new], ignore_index=True)
        df['comp_1'] = df['comp_1'].apply(lambda x: int(x.split()[1]))
        df['tree'] = df['tree'].apply(drop_extra)
        self.df_original = df.query('tree != False')
        df_for_graph = df.query('tree != False').sort_values('comp_1').query('comp_1 < 456')
        graph_usels = list(df_for_graph['tree'])
        self.nodesnumber = len(graph_usels)
        self.canvas.plot_all(graph_usels)
        self.getNodes()

    def getNodes(self):
        self.labelnumbernodes.setText(f"Количество компонентов: {self.nodesnumber}")

    def searchNode(self):
        if self.df_original is not None:
            if self.lineeditnode.text().isdigit() and int(self.lineeditnode.text()) <= 455:
                list_select = flatten(
                    self.df_original.loc[self.df_original['comp_1'] == int(self.lineeditnode.text())].values)
                if list_select:
                    self.canvas.select_nodes(list_select[1])
                    self.labelinfo.setText(gettextwithsearch(list_select))
                    self.labelinfo.show()
                else:
                    self.labelinfo.setText("Это битый компонент!")
                    self.labelinfo.show()
            if self.lineeditnode.text().isdigit() and int(self.lineeditnode.text()) > 455:
                res = int(self.lineeditnode.text()) % 455
                list_select = flatten(
                    self.df_original.loc[self.df_original['comp_1'] == res].values)
                if list_select:
                    list_b = flatten(
                        self.df_original.loc[self.df_original['comp_1'] == int(self.lineeditnode.text())].values)
                    self.canvas.select_nodes(list_select[1])
                    self.labelinfo.setText(gettextwithsearch(list_b))
                    self.labelinfo.show()
                else:
                    self.labelinfo.setText("Это битый компонент!")
                    self.labelinfo.show()



if __name__ == "__main__":
    app = QApplication([])
    win = MPLWidget()
    win.show()
    app.exec()