import sqlite3
import sys
import csv
import os
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from ui_files import tableinsp_design, entryform_design, sqlform_design, plotform_design
from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QWidget, QPushButton, QMessageBox, QShortcut, QLabel, \
    QMainWindow, QTableWidgetItem, QTableWidget

# Все возможные кодировки в python 3.11
ENCODINGS = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775',
             'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864',
             'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125',
             'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258',
             'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
             'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr',
             'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8',
             'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab',
             'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2',
             'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_32',
             'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig', 'utf-8',
             'utf8', 'utf8sig', 'utf-16', 'utf16', 'utf16le', 'utf16be', 'utf-32', 'utf32', 'utf32be', 'utf32le']


# Ошибка, которая будет вызываться, если была введена неизвестная кодировка
class UnknownEncodingError(Exception):
    pass


class TableInspector(QMainWindow, tableinsp_design.Ui_MainWindow):
    """
    Основной класс. Реализует весь основной функционал и главное окно

    Дизайн
    ------
    ui файлы были конвертированы в код и подключаются из ui_files

    Атрибуты
    ------
    paths : list
        Список всех путей открытых файлов.
        Применяется только если открыты csv файлы.
    path : str
        Конкретный путь к файлу
    mode : str
        Режим, в котором работает программа (выбирается на EntryForm).
    csv_del : str
        Разделитель csv файла
    csv_encoding : str
        Кодировка, в которой нужно открыть csv файл.
    row_added : bool
        True, если был добавлен ряд, иначе False.
        Нужен для того, чтобы метод db_table_cell_changed не вызывался лишний раз.
    query_sent : bool
        True, если был введён SQL запрос, иначе False.
        Нужен для того же, что и row_added.
    new_file_opened : bool
        True, если был открыт новый файл, иначе False.
        Нужен для того же, что и row_added и query_sent.
    files_opened : int
        Количество открытых файлов.
        Нужен для контроля кнопок (удаление/создание) при изменении режима или файла.
    pages_count : int
        Количество открытых вкладок.
        Нужен для корректного отображения названий вкладок (стр. 1, стр. 2 и т.п.).

    Методы
    ------
    initUI() :
        Инициализирует интерфейс главного окна.
    init_table() :
        После выбора режима и/или файла инициализирует таблицу.
    change_statusbar_message() :
        Изменяет сообщение в строке состояния.
    db_table_cell_changed() :
        Работает при изменении ячейки главной таблицы.
    save_csv_file() :
        Сохраняет все изменения, сделанные в уже существующем файле.
    save_new_csv_file() :
        Сохраняет созданную таблицу в csv файл.
    add_row() :
        Добавляет ряд в таблицу.
    add_col() :
        Добавляет столбец в таблицу.
        Работает только при создании своей таблицы.
    delete_row() :
        Удаляет ряд из таблицы.
    enter_sql_query() :
        Вызывает окно для ввода SQL запроса.
        Работает (логично) только если открыта БД.
    build_plot() :
        Вызывает окно с графиков.
    open_file() :
        Вызывает проводник для выбора нового файла.
    add_table() :
        Добавляет вкладку в QTabWidget.
        Работает только при просмотре csv файлов или создании своей таблицы.
    del_table() :
        Удаляет вкладку из QTabWidget.
        Работает при таких же условиях, что и add_table.
    show_instruction() :
        Открывает блокнот с руководством по использованию программы.
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_vars()

    def init_vars(self):
        """
        Загружаем интерфейс, затем вызываем форму, в которую загрузится путь к нужному файлу,
        после чего из класса этой формы вызовется функция init_table этого класса
        """

        # Дополнительные переменные для контроля программы
        self.paths = list()
        self.path = str()
        self.mode = str()
        self.csv_del = str()
        self.csv_encoding = str()
        self.row_added = False
        self.query_sent = False
        self.new_file_opened = False
        self.files_opened = 0
        self.pages_count = 1
        self.setupUi(self)
        self.helpButton.clicked.connect(self.show_instruction)
        self.openButton.clicked.connect(self.open_file)
        self.tabWidget.currentChanged.connect(self.change_statusbar_message)
        self.open_file()

    def init_table(self, source: str):
        """
        Подключаемся к ДБ (если выбрана ДБ), создаём такое же количество вкладок,
        какое количество таблиц есть в БД, заполняем их данными
        Если выбрана не БД, создаём одну вкладку,
        заполняем её данными из выбранного csv файла
        """

        self.paths = []
        if source or 'csv' in self.mode:
            self.files_opened += 1
        btn_txt = [i.text() for i in self.findChildren(QPushButton)]
        if self.tabWidget.count() > 1 or self.files_opened > 1:
            if source.split('.')[-1] in ['db', 'sqlite'] and 'Добавить таблицу' in btn_txt:
                self.addTableButton.deleteLater()
                if 'Удалить таблицу' in btn_txt:
                    self.delTableButton.deleteLater()
            if self.tableWidget.receivers(self.tableWidget.cellChanged) > 0:
                self.tableWidget.disconnect()
            for i in range(1, self.tabWidget.count()):
                self.tabWidget.removeTab(1)
            if 'csv' == source.split('.')[-1] or not source:
                self.tabWidget.setTabText(0, 'стр. 1')
                if 'Ввести SQL запрос' in btn_txt:
                    self.sqlButton.deleteLater()
            if 'Добавить столбец' in btn_txt and ('db' in source.split('.')[-1] or
                                                  'sqlite' in source.split('.')[-1] or
                                                  'csv' in source.split('.')[-1]):
                self.addColButton.deleteLater()
            self.shortcut.deleteLater()

        self.shortcut = QShortcut(QKeySequence('Ctrl+S'), self)
        if 'csv' not in self.mode and source.split('.')[-1] == 'csv':
            self.shortcut.activated.connect(self.save_csv_file)
        elif 'db' != source.split('.')[-1] and 'sqlite' != source.split('.')[-1]:
            self.shortcut.activated.connect(self.save_new_csv_file)
        if self.files_opened == 1:
            self.addButton.clicked.connect(self.add_row)
            self.delButton.clicked.connect(self.delete_row)
            self.plotButton.clicked.connect(self.build_plot)
        if source.split('/')[-1].split('.')[-1] != 'csv' and 'csv' not in self.mode:
            self.con = sqlite3.connect(source)
            self.cur = self.con.cursor()
            self.tables = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if 'Ввести SQL запрос' not in [i.text() for i in self.findChildren(QPushButton)]:
                self.sqlButton = QPushButton('Ввести SQL запрос', self)
                self.sqlButton.clicked.connect(self.enter_sql_query)
                self.verticalLayout.addWidget(self.sqlButton)
            for i in range(len(self.tables)):
                if i != 0:
                    cur_widget = QWidget(self)
                    self.tabWidget.addTab(cur_widget, self.tables[i][0])
                    cur_table = QTableWidget(cur_widget)
                else:
                    self.tabWidget.setTabText(0, self.tables[0][0])
                    cur_table = self.tableWidget
                cur_table.setGeometry(0, 0, 831, 731)
                titles = list([x[1] for x in self.cur.execute(f'PRAGMA table_info({self.tables[i][0]})').fetchall()])
                data = self.cur.execute(f'SELECT * FROM {self.tables[i][0]}').fetchall()
                fill_table(cur_table, titles, data)
                cur_table.cellChanged.connect(self.db_table_cell_changed)
                cur_table.resizeColumnsToContents()

        elif 'csv' not in self.mode:
            if 'Добавить таблицу' not in btn_txt:
                self.addTableButton = QPushButton('Добавить таблицу', self)
                self.delTableButton = QPushButton('Удалить таблицу', self)
                self.verticalLayout.addWidget(self.addTableButton)
                self.verticalLayout.addWidget(self.delTableButton)
                self.addTableButton.clicked.connect(self.add_table)
                self.delTableButton.clicked.connect(self.del_table)
            with open(source, 'r', encoding=self.csv_encoding) as f:
                reader = [row for row in csv.reader(f, delimiter=self.csv_del, skipinitialspace=True) if row]
                titles = reader[0]
                rd = reader[1::]
                fill_table(self.tableWidget, titles, rd)
                self.tableWidget.resizeColumnsToContents()
                self.tables = [rd.copy()]

        else:
            self.tables = ['стр. 1']
            self.addButton.setText('Добавить ряд')
            if 'Добавить таблицу' not in btn_txt:
                self.addTableButton = QPushButton('Добавить таблицу', self)
                self.verticalLayout.addWidget(self.addTableButton)
                self.addTableButton.clicked.connect(self.add_table)
            if 'Добавить столбец' not in btn_txt:
                self.addColButton = QPushButton('Добавить столбец', self)
                self.addColButton.clicked.connect(self.add_col)
            self.verticalLayout.insertWidget(1, self.addColButton)
            self.tableWidget.clear()
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            self.tableWidget.resizeColumnsToContents()
            self.tabWidget.setTabText(0, 'стр. 1')

        if 'csv' not in self.mode:
            self.statusBar().showMessage(
                f'Таблиц: {len(self.tables)} | '
                f'Строк: {self.tabWidget.currentWidget().children()[0].rowCount()} | '
                f'Столбцов: {self.tabWidget.currentWidget().children()[0].columnCount()}'
            )
        self.new_file_opened = False

    def change_statusbar_message(self):
        """
        Изменение сообщения в statusbar при изменении таблицы
        """

        x = self.tabWidget.currentWidget()
        self.statusBar().showMessage(
            f'Таблиц: {len(self.tables)} | '
            f'Строк: {x.children()[0].rowCount() if x is not None else 0} | '
            f'Столбцов: {x.children()[0].columnCount() if x is not None else 0}'
        )

    def db_table_cell_changed(self, row: int, col: int):
        """
        Запись в БД изменённой ячейки.
        Тут ещё куча проверок на корректность введённых данных и создавался ли новый ряд
        """

        if not self.row_added and not self.query_sent and not self.new_file_opened:
            cur_table = self.tabWidget.tabText(self.tabWidget.currentIndex())
            cur_table_widget = self.tabWidget.currentWidget().children()[0]
            cur_col = cur_table_widget.horizontalHeaderItem(col).text()
            new_val = cur_table_widget.item(row, col).text()
            try:
                if self.cur.execute(f"""SELECT Count(*) FROM {cur_table}""").fetchall()[0][0] == \
                        cur_table_widget.rowCount() and \
                        all([cur_table_widget.item(row, i).text() for i in range(cur_table_widget.columnCount())]):
                    cond = ' AND '.join([
                        f"{key} = '{val}'" for key, val in
                        {cur_table_widget.horizontalHeaderItem(i).text(): cur_table_widget.item(row, i).text()
                         for i in range(cur_table_widget.columnCount())
                         if cur_table_widget.item(row, i).text() != new_val}.items()
                    ])
                    self.cur.execute(f"""UPDATE {cur_table}
                                         SET {cur_col} = '{new_val}'
                                         WHERE {cond}""")
                    self.con.commit()
                elif all([cur_table_widget.item(row, i).text() for i in range(cur_table_widget.columnCount())]):
                    cur_table_headers = [cur_table_widget.horizontalHeaderItem(i).text()
                                         for i in range(cur_table_widget.columnCount())]
                    self.cur.execute(f"""INSERT INTO {cur_table}({','.join(cur_table_headers)})
                                         VALUES({','.join([f"'{cur_table_widget.item(row, i).text()}'"
                                                           for i in range(cur_table_widget.columnCount())])})""")
                    self.con.commit()
            except sqlite3.IntegrityError:
                QMessageBox.critical(None, 'Error',
                                     'Введены некорректные данные',
                                     QMessageBox.Ok)

    def save_csv_file(self):
        """
        Сохраняем УЖЕ СУЩЕСТВУЮЩИЙ в файл при нажатии Ctrl+S
        """

        cur_table_widget = self.tabWidget.currentWidget().children()[0]
        reader = [[cur_table_widget.horizontalHeaderItem(i).text()
                   for i in range(cur_table_widget.columnCount())]] + get_data_from_table(cur_table_widget)
        with open(self.paths[self.tabWidget.currentIndex()], 'w', encoding=self.csv_encoding) as f:
            writer = csv.writer(f, delimiter=self.csv_del)
            for i in reader:
                writer.writerow(i)

    def save_new_csv_file(self):
        """
        Сохраняем СОЗДАВАЕМЫЙ csv файл при нажатии Ctrl+S
        """

        file_name = QFileDialog.getSaveFileName(self, 'Выбрать файл для сохранения', '', 'csv files (*.csv)')[0]
        cur_table_widget = self.tabWidget.currentWidget().children()[0]
        data = get_data_from_table(cur_table_widget)
        if file_name:
            with open(file_name, 'w', encoding=self.csv_encoding) as f:
                cur_table_widget = self.tabWidget.currentWidget().children()[0]
                data = [[cur_table_widget.horizontalHeaderItem(i).text()
                         for i in range(cur_table_widget.columnCount())]] + data
                writer = csv.writer(f, delimiter=self.csv_del)
                for i in data:
                    writer.writerow(i)

    def add_row(self):
        """
        Метод добавления ряда в таблицу
        """

        self.row_added = True
        cur_table_widget = self.tabWidget.currentWidget().children()[0]
        cur_table_widget.setRowCount(cur_table_widget.rowCount() + 1)

        # Заполняем созданные ячейки таблицы, чтобы в дальнейшем избежать ошибок в других методах,
        # которые будут искать текст в этих ячейках, но получат None
        for i in range(cur_table_widget.columnCount()):
            cur_table_widget.setItem(cur_table_widget.rowCount() - 1, i, QTableWidgetItem(''))
        self.row_added = False
        self.change_statusbar_message()

    def add_col(self):
        """
        Метод добавления столбца
        """

        cur_table_widget = self.tabWidget.currentWidget().children()[0]
        cur_table_widget.setColumnCount(cur_table_widget.columnCount() + 1)
        cur_table_widget.setHorizontalHeaderLabels([str(i + 1) for i in range(cur_table_widget.columnCount())])

        # Заполняем созданные ячейки таблицы, чтобы в дальнейшем избежать ошибок в других методах,
        # которые будут искать текст в этих ячейках, но получат None
        for i in range(cur_table_widget.rowCount()):
            cur_table_widget.setItem(cur_table_widget.columnCount() - 1, i, QTableWidgetItem(''))
        self.change_statusbar_message()

    def delete_row(self):
        """
        Функция удаления ряда из таблицы
        """

        try:
            mb = QMessageBox.question(None, 'Question',
                                      'Вы уверены, что хотите удалить этот ряд?',
                                      QMessageBox.Ok | QMessageBox.Cancel)
            cur_table_widget = self.tabWidget.currentWidget().children()[0]
            cur_table = self.tabWidget.tabText(self.tabWidget.currentIndex())
            row = cur_table_widget.currentRow()
            if mb == QMessageBox.Ok and 'csv' not in self.paths[self.tabWidget.indexOf(cur_table_widget)] and\
                    len(cur_table_widget.selectedItems()) == cur_table_widget.columnCount() and \
                    'csv' not in self.mode:
                cond = ' AND '.join([
                    f"{key} = '{val}'" for key, val in
                    {cur_table_widget.horizontalHeaderItem(i).text(): cur_table_widget.item(row, i).text()
                     for i in range(cur_table_widget.columnCount())}.items()
                ])
                cur_table_widget.removeRow(row)
                self.cur.execute(f"""DELETE FROM {cur_table}
                                     WHERE {cond}""")
                self.con.commit()
            elif 'csv' in self.path or mb == QMessageBox.Ok and \
                    len(cur_table_widget.selectedItems()) == cur_table_widget.columnCount():
                cur_table_widget.removeRow(row)
            else:
                QMessageBox.warning(None, 'Warning', 'Выберите ряд!', QMessageBox.Ok | QMessageBox.Cancel)
            self.change_statusbar_message()

        except AttributeError:
            QMessageBox.warning(None, 'Warning', 'Выберите ряд!', QMessageBox.Ok | QMessageBox.Cancel)

    def enter_sql_query(self):
        """
        Показываем окно для ввода запроса
        """

        self.sql_form = SQLForm(self.con, self.cur, self)
        self.sql_form.show()

    def build_plot(self):
        """
        Вызов окна, в котором будет отображаться график
        """

        self.plot_form = PlotForm(self)
        self.plot_form.show()

    def open_file(self):
        """
        Открываем новый файл
        """

        self.new_file_opened = True
        self.entry = EntryForm(ref=self)
        self.entry.setModal(True)
        self.entry.show()

    def add_table(self):
        """
        Добавляет вкладку
        """

        self.pages_count += 1
        cur_widget = QWidget(self)
        cur_table = QTableWidget(cur_widget)
        cur_table.setGeometry(0, 0, 831, 731)
        self.tabWidget.addTab(cur_widget, f'стр. {self.pages_count}')
        self.tables.append(f'стр. {self.pages_count}')
        if 'csv' not in self.mode:
            self.entry = EntryForm(self)
            self.entry.show()

    def del_table(self):
        """
        Удаляет вкладку
        """

        mb = QMessageBox.question(None, 'Question',
                                  'Вы уверены, что хотите удалить эту вкладку?',
                                  QMessageBox.Ok | QMessageBox.Cancel)
        if mb == QMessageBox.Ok:
            self.tabWidget.removeTab(self.tabWidget.currentIndex())
            self.pages_count -= 1
            del self.paths[self.tabWidget.currentIndex()]
        if not self.tabWidget.count():
            widget = QWidget(self)
            self.tableWidget = QTableWidget(widget)
            self.tableWidget.setGeometry(0, 0, 831, 731)
            self.tabWidget.addTab(widget, 'стр. 1')

    def show_instruction(self):
        """
        Вызов инструкции к программе
        """

        command = 'notepad.exe instruction.txt'
        os.system(command)


class EntryForm(QDialog, entryform_design.Ui_entryForm):
    """
    Класс окна для выбора режима и/или файла.

    Дизайн
    ------
    ui файлы были конвертированы в код и подключаются из ui_files

    Атрибуты
    ------
    ref : QMainWindow
        Ссылка главный класс программы.
        Нужен для вызова методов главного класса.
    source : str
        Путь к файлу, с которым нужно работать.
    caller: NoneType | QPushButton
        Переменная, хранящая ссылку на объект, вызвавший этот класс.

    Методы
    ------
    load_path() :
        Загружает путь к файлу, с которым будет вестись работа.
        Также контролирует доступность полей для ввода информации.
    check_input_data() :
        Проверяет введённые данные на правильность и
        вызывает метод инициализации таблицы у главного класса программы.
    change_button_status() :
        Изменяет статус кнопки с надписью "Выбрать".
    """

    def __init__(self, ref: QMainWindow):
        super().__init__()
        self.setupUi(self)
        self.ref = ref
        self.source = str()
        self.caller = self.sender()
        self.openDialogButton.clicked.connect(self.load_path)
        self.buttonBox.rejected.connect(sys.exit)
        self.buttonBox.accepted.connect(self.check_input_data)
        self.modesBox.currentIndexChanged.connect(self.change_button_status)

    def load_path(self):
        """Загрузка пути к нужному файлу"""

        self.source = QFileDialog.getOpenFileName(self, 'Выбрать источник данных', '',
                                                  'Data Sources (*.csv *.db *.sqlite)')[0]
        if self.source.split('/')[-1].split('.')[-1] == 'csv':
            self.encodingLine.setEnabled(True)
            self.delLine.setEnabled(True)
        else:
            self.encodingLine.setEnabled(False)
            self.delLine.setEnabled(False)

    def check_input_data(self):
        """
        Куча проверок на правильность входных данных,
        затем вызов функции инициализации таблиц основного класса и закрытие окна
        """

        self.ref.mode = self.modesBox.currentText()
        if 'csv' in self.source or self.modesBox.currentText() != 'Редактирование':
            if self.delLine.text() and self.encodingLine.text():

                # Проверяем, возможно ли открыть файл, используя введённые данные
                try:
                    if not self.encodingLine.text() in ENCODINGS:
                        raise UnknownEncodingError
                    if self.modesBox.currentText() == 'Редактирование':
                        with open(self.source, 'r', encoding=self.encodingLine.text()):
                            pass
                    self.ref.csv_del = self.delLine.text()
                    self.ref.csv_encoding = self.encodingLine.text()
                    if self.caller is None or self.caller.text() != 'Добавить таблицу':
                        self.ref.init_table(self.source)
                    else:
                        table = self.ref.tabWidget.widget(self.ref.tabWidget.count() - 1).children()[0]
                        with open(self.source, 'r', encoding=self.encodingLine.text()) as f:
                            reader = [row for row in csv.reader(f, delimiter=self.delLine.text()) if row]
                            titles = reader[0]
                        fill_table(table, titles, reader[1::])
                    self.close()
                except UnknownEncodingError:
                    QMessageBox.critical(None, 'Error', 'Неизвестная кодировка', QMessageBox.Ok)
                except UnicodeError:
                    QMessageBox.critical(None, 'Error', 'Невозможно прочитать файл в данной кодировке', QMessageBox.Ok)
            else:
                QMessageBox.critical(None, 'Error', 'Нужно заполнить все поля!', QMessageBox.Ok)
            self.ref.paths.append(self.source)
        elif self.source or self.modesBox.currentText() == 'Создание csv':
            self.ref.init_table(self.source)
            if self.modesBox.currentText() != 'Создание csv':
                self.ref.paths.append(self.source)
            self.close()
        elif self.modesBox.currentText() != 'Создание csv':
            QMessageBox.critical(None, 'Error', 'Выберите файл!', QMessageBox.Ok)

    def change_button_status(self):
        """Просто изменяет статус кнопки с надписью 'Выбрать'"""

        if self.modesBox.currentText() == 'Редактирование':
            self.openDialogButton.setEnabled(True)
            self.encodingLine.setEnabled(False)
            self.delLine.setEnabled(False)
        else:
            self.openDialogButton.setEnabled(False)
            self.encodingLine.setEnabled(True)
            self.delLine.setEnabled(True)


class SQLForm(QMainWindow, sqlform_design.Ui_MainWindow):
    """
    Класс, реализующий окно для ввода SQL запроса.

    Дизайн
    ------
    ui файлы были конвертированы в код и подключаются из ui_files

    Атрибуты
    ------
    con : sqlite3.Connection
        Соединение с базой данных.
    cur : sqlite3.Cursor
        Объект курсора базы данных.
    ref : QMainWindow
        Ссылка на главный класс программы.

    Методы
    ------
    send_sql_query() :
        Проверка ведённых данных на корректность и отправка SQL запроса.
    """

    def __init__(self, con: sqlite3.Connection, cur: sqlite3.Cursor, ref: QMainWindow):
        super().__init__()
        self.con = con
        self.cur = cur
        self.ref = ref
        self.setupUi(self)
        self.enterButton.clicked.connect(self.send_sql_query)

    def send_sql_query(self):
        """
        Отправляем запрос
        """

        self.ref.query_sent = True
        try:
            self.cur.execute(self.sqlTextEdit.toPlainText())
            cur_table_widget = self.ref.tabWidget.currentWidget().children()[0]
            cur_table = self.ref.tabWidget.tabText(self.ref.tabWidget.currentIndex())
            titles = list([x[1] for x in self.cur.execute(f'PRAGMA table_info({cur_table})').fetchall()])
            data = self.cur.execute(f'SELECT * FROM {cur_table}').fetchall()
            fill_table(cur_table_widget, titles, data)
            self.con.commit()
        except sqlite3.OperationalError:
            QMessageBox.critical(None, 'Error', 'Неверный запрос', QMessageBox.Ok)
        self.ref.query_sent = False


class PlotForm(QWidget, plotform_design.Ui_Form):
    """
    Класс, реализующий окно для вывода графика.

    Дизайн
    ------
    ui файлы были конвертированы в код и подключаются из ui_files

    Атрибуты
    ------
    ref : QMainWindow
        Ссылка на главный класс программы.

    Методы
    ------
    build_plot() :
        Строит, сохраняет график, построенный по выбранным столбцам.
    show_plot() :
        Вызывает класс PlotWindow.
    """

    def __init__(self, ref: QMainWindow):
        super().__init__()
        self.ref = ref
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.build_plot)
        self.buttonBox.rejected.connect(self.close)
        self.curr = self.ref.tabWidget.currentWidget().children()[0]
        self.headers = [self.curr.horizontalHeaderItem(i).text() for i in range(self.curr.columnCount())]
        for header in self.headers:
            self.axisXComboBox.addItem(header)
            self.axisYComboBox.addItem(header)

    def build_plot(self):
        """
        Построение графика.
        Выделяем данные из столбцов, передаём их в функции seaborn
        """

        x = self.axisXComboBox.currentText()
        y = self.axisYComboBox.currentText()
        col_x = self.headers.index(x)
        data_x = [self.curr.item(row_x, col_x).text()
                  if not self.curr.item(row_x, col_x).text().replace('.', '', 1).isdigit()
                  else float(self.curr.item(row_x, col_x).text())
                  for row_x in range(self.curr.rowCount())]

        col_y = self.headers.index(y)
        data_y = [self.curr.item(row_y, col_y).text()
                  if not self.curr.item(row_y, col_y).text().replace('.', '', 1).isdigit()
                  else float(self.curr.item(row_y, col_y).text())
                  for row_y in range(self.curr.rowCount())]

        check_int_values_y = all([type(i) in (int, float) for i in data_y])
        check_int_values_x = all([type(j) in (int, float) for j in data_x])
        name = f'./plots/{x}_to_{y}.png'

        try:
            plot = sns.lineplot(x=data_x, y=data_y) \
                if check_int_values_y and check_int_values_x \
                else sns.barplot(x=data_x, y=data_y)
            plot.set_xlabel(x)
            plot.set_ylabel(y)
            plt.savefig(name)
            plt.close()
            self.show_plot(name)
            self.close()
        except TypeError:
            QMessageBox.critical(None, 'Error', 'Ни один столбец не заполнен числами полностью', QMessageBox.Ok)

    def show_plot(self, name: str):
        """
        Показываем окно с графиком
        """

        self.plot_window = PlotWindow(name)
        self.plot_window.show()


class PlotWindow(QMainWindow):
    """
    Класс, реализующий окно для вывода графика на экран.

    Дизайн
    ------
    ui файлы были конвертированы в код и подключаются из ui_files

    Атрибуты
    ------
    file : str
        Хранит название картинки, в которой сохранён график.
    width : int
        Ширина картинки.
    height : int
        Высота картинки.
    pixmap : QPixmap
        Хранит само изображение.
    lbl : QLabel
        Виджет, выводящий переданное ему изображение на экран.

    Методы
    ------
    initUI() :
        Инициализирует интерфейс.
    keyPressEvent() :
        Обрабатывает нажатие клавиш.
        Работает при нажатии UpArrow и DownArrow (увеличивает/уменьшает масштаб изображения)
    mousePressEvent() :
        Обрабатывает нажатие кнопок мыши.
        Работает если нажата LMB.
    mouseReleaseEvent() :
        Обрабатывает событие отпускания кнопки мыши.
    mouseMoveEvent() :
        Обрабатывает движение мыши.
        Работает только при зажатом LMB.
    """

    def __init__(self, file: str):
        super().__init__()
        self.file = file
        self.width, self.height = Image.open(self.file).size
        self.pixmap = QPixmap(self.file)
        self.lbl = QLabel(self)
        self.initUI()

    def initUI(self):
        """
        Размещаем изображение графика на окне
        """

        self.setGeometry(30, 30, self.width, self.height)
        self.lbl.resize(self.width, self.height)
        self.lbl.move(0, 0)
        self.lbl.setPixmap(self.pixmap)
        self.setMouseTracking(True)
        self.mouse_button = None
        self.distance = []

    def keyPressEvent(self, event):
        """
        Увеличиваем картинку, если нажата стрелка вверх,
        уменьшаем, если нажата стрелка вниз
        """

        if event.key() == Qt.Key_Up:
            self.width += int(50 * self.width / self.height)
            self.height += 50
        elif event.key() == Qt.Key_Down:
            self.width -= int(50 * self.width / self.height)
            self.height -= 50
        self.lbl.setPixmap(self.pixmap.scaled(self.width, self.height))
        self.lbl.resize(self.width, self.height)

    def mousePressEvent(self, event):
        """
        Фиксируем расстояние от курсора до левого верхнего угла картинки
        """

        self.mouse_button = event.button()
        self.distance = [event.x() - self.lbl.x(), event.y() - self.lbl.y()]

    def mouseReleaseEvent(self, event):
        """
        Если ЛКМ отжата, то необходимо обнулить переменную, хранящую название нажатой кнопки мыши
        """

        self.mouse_button = None

    def mouseMoveEvent(self, event):
        """
        Двигаем картинку за курсором
        """

        if self.mouse_button == Qt.LeftButton:
            self.lbl.move(event.x() - self.distance[0], event.y() - self.distance[1])


def fill_table(table: QTableWidget, titles: list[str], data: list[list[str]]):
    """
    Функция заполнения таблицы QTableWidget
    """

    table.setRowCount(len(data))
    table.setColumnCount(len(titles))
    table.setHorizontalHeaderLabels(titles)
    for y, elem in enumerate(data):
        for x, val in enumerate(elem):
            table.setItem(y, x, QTableWidgetItem(str(val)))


def get_data_from_table(cur_table_widget: QObject) -> list[list]:
    """
    Собирает информацию из таблицы
    :return: Список списков, представляющих собой ряды таблицы
    """

    data, half = list(), list()
    for i in range(cur_table_widget.rowCount()):
        for j in range(cur_table_widget.columnCount()):
            half.append(cur_table_widget.item(i, j).text())
        data.append(half)
        half = []
    return data


def except_hook(cls, exception, traceback):
    """
    Ловим ошибки
    """

    sys.__excepthook__(cls, exception, traceback)


# ЗАПУСК
if __name__ == '__main__':
    app = QApplication(sys.argv)
    tipy = TableInspector()
    tipy.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
