import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem


class DBSample(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.go_redactor.clicked.connect(self.openWindow)
        self.connection = sqlite3.connect("coffee.sqlite")
        self.pushButton.clicked.connect(self.res)
        res = self.connection.cursor().execute("""SELECT ID,
       название_сорта,
       степень_обжарки,
       молотый_или_в_зернах,
       описание_вкуса,
       цена,
       объем_упаковки
  FROM all_information""").fetchall()
        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'название сорта', 'степень обжарки',
                                                    ' молот./в зернах', 'описание вкуса', 'цена', 'объем упаковки'])
        self.tableWidget.setRowCount(0)
        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        # При закрытии формы закроем и наше соединение
        # с базой данных
        self.connection.close()

    def res(self):
        res = self.connection.cursor().execute("""SELECT ID,
               название_сорта,
               степень_обжарки,
               молотый_или_в_зернах,
               описание_вкуса,
               цена,
               объем_упаковки
          FROM all_information""").fetchall()
        # Заполним размеры таблицы
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'название сорта', 'степень обжарки',
                                                    ' молот./в зернах', 'описание вкуса', 'цена', 'объем упаковки'])
        self.tableWidget.setRowCount(0)
        # Заполняем таблицу элементами
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

    def openWindow(self):
        self.az = Redactor()
        self.az.show()


class Redactor(QMainWindow):
    def __init__(self, parent=None):
        super(Redactor, self).__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.titles = None
        self.con = sqlite3.connect("coffee.sqlite")
        self.table2.itemChanged.connect(self.item_changed)
        self.modified = {}
        self.push_restart.clicked.connect(self.restart)
        self.push_update.clicked.connect(self.update)
        self.push_add.clicked.connect(self.add)
        self.len = 0

    def restart(self):
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM all_information WHERE id=?",
                             (item_id := self.spinBox.text(),)).fetchall()
        if not result:
            self.statusBar().showMessage('Ничего не нашлось')
            return
        else:
            self.statusBar().showMessage(f"Нашлась запись с id = {item_id}")
        self.table2.setRowCount(len(result))
        self.table2.setColumnCount(len(result[0]))
        r = cur.execute("SELECT * FROM all_information").fetchall()
        self.len = len(r)
        self.titles = [description[0] for description in cur.description]
        self.table2.setHorizontalHeaderLabels(['ID', 'название сорта', 'степень обжарки',
                                               'молот./в зернах', 'описание вкуса', 'цена', 'объем упаковки'])
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.table2.setItem(i, j, QTableWidgetItem(str(val)))
        self.modified = {}

    def item_changed(self, item):
        self.modified[self.titles[item.column()]] = item.text()

    def update(self):
        if self.modified:
            cur = self.con.cursor()
            que = "UPDATE all_information SET\n"
            for key in self.modified.keys():
                que += "{}='{}'\n".format(key, self.modified.get(key))
                que += "WHERE id = ?"
                cur.execute(que, (self.spinBox.text(),))
            self.con.commit()
            self.modified.clear()

    def add(self):
        cur = self.con.cursor()
        text = self.lineEdit.text().split(',')
        if len(text) == 6:
            f = f"INSERT INTO all_information VALUES ({self.len + 1}, '{text[0]}', '{text[1]}', '{text[2]}'," \
                f" '{text[3]}', {text[4]}, {text[5]})"
            self.statusBar().showMessage(f"Добавлена запись с id = {self.len + 1}")
            cur.execute(f)
            self.con.commit()
        else:
            self.statusBar().showMessage(f"Неверное количество значений")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DBSample()
    ex.show()
    sys.exit(app.exec())
