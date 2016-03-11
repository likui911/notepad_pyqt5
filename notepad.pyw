import ctypes
import configparser
import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

"""仿照Windows系统自带记事本(Nodepad)
   @http://my.oschina.net/upy
"""

CONFIG_FILE_PATH = "notepad.ini"
# 解决任务栏图标问题
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("notepad")
QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("utf-8"))


class Notepad(QtWidgets.QMainWindow):
    def __init__(self):
        self.judgeConfig()
        # 当前文件名
        self.cur_file = ''
        # 默认文件夹
        self.default_dir = ''
        # 系统剪切板
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.last_search = ''
        # 字体设置
        self.font_family = 'Consolas'
        self.font_size = '16'
        self.font_bold = 'False'
        self.font_italic = 'False'
        self.font_strikeOut = 'False'
        self.font_underline = 'False'
        self.config = configparser.ConfigParser()
        self.config.read(CONFIG_FILE_PATH, 'utf-8')
        super(QtWidgets.QMainWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('无标题 - 记事本')
        self.setWindowIcon(QtGui.QIcon('resource/notepad.png'))
        self.statusBar().showMessage('Ready')
        # 创建编辑区
        self.createEditText()
        self.createActions()
        self.createMenubar()
        self.createToolbar()
        self.readSettings()

        self.cutAction.setEnabled(False)
        self.copyAction.setEnabled(False)
        self.undoAction.setEnabled(False)
        self.redoAction.setEnabled(False)
        self.text.copyAvailable.connect(self.cutAction.setEnabled)
        self.text.copyAvailable.connect(self.copyAction.setEnabled)
        self.text.undoAvailable.connect(self.undoAction.setEnabled)
        self.text.redoAvailable.connect(self.redoAction.setEnabled)
        self.text.textChanged.connect(self.findEnable)

    def findEnable(self):
        # 当textEdit不为空时，findAction才生效
        if self.text.toPlainText():
            self.findAction.setEnabled(True)
        else:
            self.findAction.setEnabled(False)
            self.findNextAction.setEnabled(False)

    def createEditText(self):
        self.text = QtWidgets.QPlainTextEdit()
        # 必须setContextMenuPolicy为CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text.customContextMenuRequested.connect(self.showContextMenu)
        self.setCentralWidget(self.text)

    def showContextMenu(self):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.undoAction)
        menu.addAction(self.redoAction)
        menu.addSeparator()
        menu.addAction(self.cutAction)
        menu.addAction(self.copyAction)
        menu.addAction(self.pasteAction)
        menu.addSeparator()
        menu.addAction(self.selectAllAction)

        # 在指定坐标弹出菜单
        menu.exec_(QtGui.QCursor.pos())

    def judgeConfig(self):
        # 如果配置文件不存在，则新建
        if not os.path.exists(CONFIG_FILE_PATH):
            f = open(CONFIG_FILE_PATH, 'w', encoding='utf-8')
            f.close()

    def readSettings(self):
        # 调节窗口大小
        width = self.getConfig('Display', 'width', 800)
        height = self.getConfig('Display', 'height ', 600)
        px = self.getConfig('Display', 'x', 0)
        py = self.getConfig('Display', 'y', 0)
        self.move(int(px), int(py))
        self.resize(int(width), (height))

        self.default_dir = self.getConfig('Setting', 'dir', '')

        self.font_family = self.getConfig('Font', 'family', 'Consolas')
        self.font_size = self.getConfig('Font', 'size', '10')
        self.font_bold = self.getConfig('Font', 'bold', '0')
        self.font_italic = self.getConfig('Font', 'italic', '0')
        self.font_strikeOut = self.getConfig('Font', 'strikeOut', '0')
        self.font_underline = self.getConfig('Font', 'underline', '0')
        font = QtGui.QFont(self.font_family, int(self.font_size))
        font.setBold(int(self.font_bold))
        font.setItalic(int(self.font_italic))
        font.setStrikeOut(int(self.font_strikeOut))
        font.setUnderline(int(self.font_underline))
        self.text.setFont(font)

    def writeSetting(self):
        # 窗口位置信息
        self.writeConfig('Display', 'width', str(self.size().width()))
        self.writeConfig('Display', 'height', str(self.size().height()))
        self.writeConfig('Display', 'x', str(self.pos().x()))
        self.writeConfig('Display', 'y', str(self.pos().y()))

        self.writeConfig('Setting', 'dir', self.default_dir)

        self.writeConfig('Font', 'family', self.text.font().family())
        self.writeConfig('Font', 'size', str(self.text.font().pointSize()))
        self.writeConfig('Font', 'bold', int(self.text.font().bold()))
        self.writeConfig('Font', 'italic', int(self.text.font().italic()))
        self.writeConfig('Font', 'strikeOut', int(self.text.font().strikeOut()))
        self.writeConfig('Font', 'underline', int(self.text.font().underline()))

        # 写入文件
        self.config.write(open(CONFIG_FILE_PATH, 'w', encoding='utf-8'))

    def createMenubar(self):
        fileMenu = QtWidgets.QMenu('文件', self)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitAction)
        editMenu = QtWidgets.QMenu('编辑', self)
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addSeparator()

        # 暂时将find、findnex设置为无效，有效时再激活
        self.findAction.setEnabled(False)
        self.findNextAction.setEnabled(False)

        editMenu.addAction(self.findAction)
        editMenu.addAction(self.findNextAction)
        editMenu.addAction(self.replaceAction)

        styleMenu = QtWidgets.QMenu('格式', self)
        styleMenu.addAction(self.lineWrapAction)
        styleMenu.addAction(self.fontAction)
        helpMenu = QtWidgets.QMenu('帮助', self)
        helpMenu.addAction(self.aboutAction)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(editMenu)
        self.menuBar().addMenu(styleMenu)
        self.menuBar().addMenu(helpMenu)

    def createToolbar(self):
        toolbar = self.addToolBar('File')
        toolbar.addAction(self.newAction)
        toolbar.addAction(self.openAction)
        toolbar.addAction(self.saveAction)
        toolbar.addSeparator()
        toolbar.addAction(self.cutAction)
        toolbar.addAction(self.copyAction)
        toolbar.addAction(self.pasteAction)

    def createActions(self):
        self.undoAction = QtWidgets.QAction(QtGui.QIcon('resource/undo.png'), "撤销", self,
                                            shortcut=QtGui.QKeySequence.Undo,
                                            statusTip="撤销编辑",
                                            triggered=self.text.undo)
        self.redoAction = QtWidgets.QAction(QtGui.QIcon('resource/redo.png'), '重做', self,
                                            shortcut=QtGui.QKeySequence.Redo,
                                            statusTip='重做编辑',
                                            triggered=self.text.redo)
        self.cutAction = QtWidgets.QAction(QtGui.QIcon('resource/cut.png'), "剪切", self,
                                           shortcut=QtGui.QKeySequence.Cut,
                                           statusTip="剪切选中文本",
                                           triggered=self.text.cut)
        self.copyAction = QtWidgets.QAction(QtGui.QIcon('resource/copy.png'), "复制", self,
                                            shortcut=QtGui.QKeySequence.Copy,
                                            statusTip="复制选中文本",
                                            triggered=self.text.copy)
        self.pasteAction = QtWidgets.QAction(QtGui.QIcon('resource/paste.png'), "粘贴", self,
                                             shortcut=QtGui.QKeySequence.Paste,
                                             statusTip="撤销编辑",
                                             triggered=self.text.paste)
        self.selectAllAction = QtWidgets.QAction(QtGui.QIcon('resource/SelectAll.png'), "全选", self,
                                                 shortcut=QtGui.QKeySequence.SelectAll,
                                                 statusTip="全部选择",
                                                 triggered=self.text.selectAll)
        self.newAction = QtWidgets.QAction(QtGui.QIcon('resource/new.png'), '新建', self,
                                           shortcut=QtGui.QKeySequence.New,
                                           statusTip='新建文本',
                                           triggered=self.newFile)
        self.openAction = QtWidgets.QAction(QtGui.QIcon('resource/open.png'), '打开', self,
                                            shortcut=QtGui.QKeySequence.Open,
                                            statusTip='打开文件',
                                            triggered=self.openFile)
        self.saveAction = QtWidgets.QAction(QtGui.QIcon('resource/save.png'), '保存', self,
                                            shortcut=QtGui.QKeySequence.Save,
                                            statusTip='保存到磁盘',
                                            triggered=self.saveFile)
        self.saveAsAction = QtWidgets.QAction(QtGui.QIcon('resource/save.png'), '另存为', self,
                                              shortcut=QtGui.QKeySequence.SaveAs,
                                              statusTip='文件另存为',
                                              triggered=self.saveAsFile)
        self.quitAction = QtWidgets.QAction(QtGui.QIcon('resource/exit.png'), '退出', self,
                                            shortcut="Ctrl+Q",
                                            statusTip='退出',
                                            triggered=self.close)
        self.lineWrapAction = QtWidgets.QAction(QtGui.QIcon('resource/check.png'), '自动换行', self,
                                                triggered=self.setLineWrap)
        self.fontAction = QtWidgets.QAction(QtGui.QIcon('resource/font.png'), '字体', self,
                                            statusTip='设置字体',
                                            triggered=self.setFont)
        self.aboutAction = QtWidgets.QAction(QtGui.QIcon('resource/about.png'), '关于', self, statusTip='关于',
                                             triggered=self.about)
        self.findAction = QtWidgets.QAction(QtGui.QIcon('resource/find.png'), '查找', self, statusTip='查找',
                                            shortcut='Ctrl+F',
                                            triggered=self.findText)
        self.findNextAction = QtWidgets.QAction(QtGui.QIcon('resource/find.png'), '查找下一个', self, statusTip='查找下一个',
                                                shortcut='F3',
                                                triggered=self.searchText)
        self.replaceAction = QtWidgets.QAction(QtGui.QIcon('resource/replace.png'), '替换', self, statusTip='替换',
                                               shortcut='Ctrl+H',
                                               triggered=self.replace)

    def closeEvent(self, event):
        if self.maybeSave():
            # 关闭窗口时保存配置信息
            self.writeSetting()
            event.accept()
        else:
            event.ignore()

    def newFile(self):
        if self.maybeSave():
            self.text.clear()

    def openFile(self):
        if self.maybeSave():
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, '', self.default_dir, '文本 (*.txt);;所有文件(*.*)')
            file = QtCore.QFile(filename)
            if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                return
            inf = QtCore.QTextStream(file)
            self.text.setPlainText(inf.readAll())
            self.setCurrentFile(filename)

    def saveFile(self):
        if not self.cur_file:
            return self.saveAsFile()
        writer = QtGui.QTextDocumentWriter(self.cur_file)
        success = writer.write(self.text.document())
        self.setCurrentFile(self.cur_file)
        if success:
            self.statusBar().showMessage('保存成功', 1000)
        return success

    def saveAsFile(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, '', self.default_dir + '无标题', '文本 (*.txt);;所有文件(*.*)')
        # 如果取消保存，不要向下执行
        if not filename:
            return False
        self.setCurrentFile(filename)
        return self.saveFile()

    def getConfig(self, section, key, default):
        # 返回配置信息，如果获取失败返回默认值
        try:
            return self.config[section][key]
        except:
            return default

    def findText(self):
        self.find_dialog = QtWidgets.QDialog(self)
        self.find_dialog.setWindowTitle('查找')
        search_label = QtWidgets.QLabel('查找：')
        self.search_text = QtWidgets.QLineEdit(self.last_search)
        search_label.setBuddy(self.search_text)
        self.search_btn = QtWidgets.QPushButton('查找下一个')
        self.search_btn.setDefault(True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(search_label)
        layout.addWidget(self.search_text)
        layout.addWidget(self.search_btn)

        self.search_btn.clicked.connect(self.searchText)
        self.find_dialog.setLayout(layout)
        self.find_dialog.show()

    def searchText(self):
        cursor = self.text.textCursor()
        start = cursor.anchor()
        text = self.search_text.text()
        # 上一次查找的字符串
        self.last_search = text
        # 根据条件判断是否激活findNextAction
        if self.last_search:
            self.findNextAction.setEnabled(True)
        text_len = len(text)
        context = self.text.toPlainText()
        # 先在文本中进行查找，判断字符串是否存在
        index = context.find(text, start)
        if -1 == index:
            QtWidgets.QMessageBox.information(self.find_dialog, '记事本', '找不到\"%s\"' % text)
        else:
            start = index
            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            # 向右多移动字符串长度
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, start + text_len)
            # 同时anchor、position同时左移字符串长度
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, text_len)
            cursor.selectedText()
            self.text.setTextCursor(cursor)

    def replaceText(self):
        cursor = self.text.textCursor()
        start = cursor.anchor()
        text = self.search_text.text()
        text_len = len(text)
        context = self.text.toPlainText()
        index = context.find(text, start)
        sender = self.sender()
        # 如果sender是替换按钮，替换选中文字
        if sender is self.replace_button:
            if text == cursor.selectedText():
                position = cursor.anchor()
                cursor.removeSelectedText()
                replace_text = self.replace_text.text()
                cursor.insertText(replace_text)
                # 替换文字后要重新搜索，这个时候cursor还未修改
                self.replaceText()
                return
        if -1 == index:
            QtWidgets.QMessageBox.information(self.replace_dialog, '记事本', '找不到\"%s\"' % text)
        else:
            start = index
            cursor = self.text.textCursor()
            cursor.clearSelection()
            cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, start + text_len)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, text_len)
            cursor.selectedText()
            self.text.setTextCursor(cursor)

    def replaceAll(self):
        # 无法撤销，需要做下撤销
        text = self.search_text.text()
        replace_text = self.replace_text.text()
        context = self.text.toPlainText()
        new_context = context.replace(text, replace_text)
        self.text.setPlainText(new_context)

    def replace(self):
        self.replace_dialog = QtWidgets.QDialog(self)
        self.replace_dialog.setWindowTitle('替换')
        search_label = QtWidgets.QLabel('查找内容：')
        self.search_text = QtWidgets.QLineEdit()
        search_label.setBuddy(self.search_text)
        replace_label = QtWidgets.QLabel('替换为：')
        # 默认替换为空格
        self.replace_text = QtWidgets.QLineEdit()
        replace_label.setBuddy(self.replace_text)
        self.find_button = QtWidgets.QPushButton('查找下一个')
        self.replace_button = QtWidgets.QPushButton('替换')
        self.replace_all_button = QtWidgets.QPushButton('全部替换')

        self.replace_button.setEnabled(False)
        self.replace_all_button.setEnabled(False)

        self.find_button.clicked.connect(self.replaceText)
        self.replace_button.clicked.connect(self.replaceText)
        self.replace_all_button.clicked.connect(self.replaceAll)
        self.search_text.textChanged.connect(self.replaceEnable)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(search_label, 0, 0)
        layout.addWidget(self.search_text, 0, 1)
        layout.addWidget(self.find_button, 0, 2)
        layout.addWidget(replace_label, 1, 0)
        layout.addWidget(self.replace_text, 1, 1)
        layout.addWidget(self.replace_button, 1, 2)
        layout.addWidget(self.replace_all_button, 2, 2)
        self.replace_dialog.setLayout(layout)
        self.replace_dialog.show()

    def replaceEnable(self):
        if not self.search_text.text():
            self.replace_button.setEnabled(False)
            self.replace_all_button.setEnabled(False)
        else:
            self.replace_button.setEnabled(True)
            self.replace_all_button.setEnabled(True)

    def maybeSave(self):
        # 如果文件有修改，弹出对话框，提示用户是否保存
        if self.text.document().isModified():
            alert = QtWidgets.QMessageBox(self)
            alert.setWindowTitle('记事本')
            alert.setText('是否将更改保存到 %s ？' % self.cur_file)
            saveButton = alert.addButton('保存', QtWidgets.QMessageBox.ActionRole)
            unSaveButton = alert.addButton('不保存', QtWidgets.QMessageBox.ActionRole)
            cancelButton = alert.addButton('取消', QtWidgets.QMessageBox.ActionRole)
            alert.exec_()

            ret = alert.clickedButton()
            if ret == saveButton:
                return self.saveFile()
            elif ret == unSaveButton:
                return True
            elif ret == cancelButton:
                return False
        return True

    def about(self):
        QtWidgets.QMessageBox.about(
            self, '关于', r'<h2>记事本</h2><p> <b>一个简单的记事本程序。</b><br>基于Python 3.x PyQt5.x 开发<br>likui_911@163.com</p>')

    def setLineWrap(self):
        if not self.text.lineWrapMode():
            self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
            self.lineWrapAction.setIcon(QtGui.QIcon('resource/check.png'))
        else:
            self.text.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
            self.lineWrapAction.setIcon(QtGui.QIcon(''))

    def setFont(self):
        # 默认选择当前字体
        font, ok = QtWidgets.QFontDialog.getFont(self.text.font(), self, '字体')
        if ok:
            self.text.setFont(QtGui.QFont(font))

    def setCurrentFile(self, filename):
        self.cur_file = filename
        path, _ = os.path.split(filename)
        self.default_dir = path + '/'
        if not filename:
            self.setWindowTitle('无标题 - 记事本')
        else:
            self.setWindowTitle('%s - 记事本' % filename)
        self.text.document().setModified(False)

    def writeConfig(self, section, key, value):
        # 向config写入信息
        if not self.config.has_section(section):
            self.config.add_section(section)
        # value必须是str，否则会抛TypeError
        self.config.set(section, key, str(value))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    translator = QtCore.QTranslator()
    if len(sys.argv) > 1:
        locale = sys.argv[1]
    else:
        locale = QtCore.QLocale.system().name()

    translator.load('qt_%s' % locale,
                    QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    # 切换语言，主要针对系统窗口如字体选择
    app.installTranslator(translator)
    notepad = Notepad()
    notepad.show()
    app.exec_()
