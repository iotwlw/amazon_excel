import os
import sys
import json
import random
import pandas as pd
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from ui.ui_main import Ui_MainWindow
from mylogclass import MyLogClass
from db_class import db_class


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.setFixedSize(self.width(), self.height())

        self.log = MyLogClass()
        self.db = db_class()
        self.settings = QSettings("HKEY_CURRENT_USER\\Software\\amazon_excel", QSettings.NativeFormat)  # 环境变量

        self.signals()
        self.load_settings()

    def signals(self):
        self.pushButton_excel.clicked.connect(lambda: self.open_file(self.lineEdit_excel, 'Excel (*.xls;*.xlsx)'))
        self.pushButton_set.clicked.connect(self.save_settings)
        self.pushButton_run.clicked.connect(self.run)

    # 槽函数-----------------------------------------------------------------------------------------------------------
    # 打开文件
    def open_file(self, lineEdit, file_type):
        try:
            filenames, _ = QFileDialog.getOpenFileNames(self, '选取文件', './', file_type)
            lineEdit.setText(json.dumps(filenames, ensure_ascii=False))
        except Exception as e:
            self.log.logger.warning(str(e))

    # 载入注册表设置
    def load_settings(self):
        self.settings.setValue('.', '-')
        v1 = self.settings.value("v1", 'New')
        v2 = self.settings.value("v2", '3')
        v3 = self.settings.value("v3", '99')
        v4 = self.settings.value("v4", 'FBM')
        v5 = self.settings.value("v5", 'Normal')
        v6 = self.settings.value("v6", '4')
        s1 = self.settings.value("s1", '0')
        s2 = self.settings.value("s2", 'FBA,FBM')
        s3 = self.settings.value("s3", '是,无商标')
        self.lineEdit_1.setText(v1)
        self.lineEdit_2.setText(v2)
        self.lineEdit_3.setText(v3)
        self.lineEdit_4.setText(v4)
        self.lineEdit_5.setText(v5)
        self.lineEdit_6.setText(v6)
        self.lineEdit_s1.setText(s1)
        self.lineEdit_s2.setText(s2)
        self.lineEdit_s3.setText(s3)

    # 保存注册表设置
    def save_settings(self):
        v1 = self.lineEdit_1.text()
        v2 = self.lineEdit_2.text()
        v3 = self.lineEdit_3.text()
        v4 = self.lineEdit_4.text()
        v5 = self.lineEdit_5.text()
        v6 = self.lineEdit_6.text()
        s1 = self.lineEdit_s1.text()
        s2 = self.lineEdit_s2.text()
        s3 = self.lineEdit_s3.text()
        self.settings.setValue('v1', v1)
        self.settings.setValue('v2', v2)
        self.settings.setValue('v3', v3)
        self.settings.setValue('v4', v4)
        self.settings.setValue('v5', v5)
        self.settings.setValue('v6', v6)
        self.settings.setValue('s1', s1)
        self.settings.setValue('s2', s2)
        self.settings.setValue('s3', s3)
        QMessageBox.information(self, '提示', '保存成功')

    # 表格拆分 保存
    def df_split(self, df, path):
        df1 = df[(df.跟卖 == '是') | (df.跟卖 == '无商标')]
        df2 = df[df.跟卖 == '否']
        df3 = df[df.跟卖 == '多商品']
        df1 = df1.dropna(axis=0)
        df2 = df2.dropna(axis=0)
        df3 = df3.dropna(axis=0)
        filename = os.path.splitext(path)
        df1.to_excel(filename[0] + '_是或无商标' + filename[1], index=False)
        df2.to_excel(filename[0] + '_否' + filename[1], index=False)
        df3.to_excel(filename[0] + '_多商品' + filename[1], index=False)

    # 得到筛选条件
    def get_where(self, price: str, send: str, sell: str) -> str:
        send = '|'.join(["(df.配送方式 == '" + li + "')" for li in send.split(',')])
        sell = '|'.join(["(df.跟卖 == '" + li + "')" for li in sell.split(',')])
        where = '(df.价格 > {}) & ({}) & ({})'.format(price, send, sell)
        return where

    # 得到20位随机字符串
    def get_sku(self) -> str:
        sss = '0123456789qwertyuiopasdfghjklmnbvcxz'
        txt = ''
        for i in range(20):
            txt += random.choice(sss)
        result = self.db.insert(txt)
        if result:
            return txt
        else:
            return self.get_sku()

    # 生成主逻辑
    def run(self):
        try:
            v1 = self.lineEdit_1.text()
            v2 = self.lineEdit_2.text()
            v3 = self.lineEdit_3.text()
            v4 = self.lineEdit_4.text()
            v5 = self.lineEdit_5.text()
            v6 = self.lineEdit_6.text()
            d1 = self.dateTimeEdit_1.text()
            d2 = self.dateTimeEdit_2.text()
            price = self.lineEdit_s1.text()
            send = self.lineEdit_s2.text()
            sell = self.lineEdit_s3.text()

            path_excel = self.lineEdit_excel.text()
            if not path_excel: return
            path_list = json.loads(path_excel, encoding='utf8')
            for path in path_list:
                df = pd.read_excel(path)
                self.df_split(df, path)

                df['价格'] = df['价格'].str.replace('$', '').astype('float')
                where = self.get_where(price, send, sell)
                df = df[eval(where)]
                datas = []
                for li in df.itertuples():
                    sku = self.get_sku()
                    asin = li.ASIN
                    zhuangkuang = v1
                    jiage = li.价格 - float(v2)
                    kucun = v3
                    fahuo = v4
                    genmai = v5
                    mai = d1
                    xia = d2
                    beihuo = v6
                    datas.append([sku, asin, zhuangkuang, jiage, kucun, fahuo, genmai, mai, xia, beihuo])
                df = pd.DataFrame(datas,
                                  columns=['自定义SKU', 'ASIN（子Asin）', '物品状况', '价格', '库存数量',
                                           '发货方式', '跟卖方式', '跟卖时间', '下架时间', '备货周期(天)'])
                filename = os.path.splitext(path)
                df.to_csv(filename[0] + '_导出.csv', index=False, encoding='utf8')
            QMessageBox.information(self, '提示', '运行完成')
        except Exception as e:
            QMessageBox.warning(self, '错误', str(e))
            self.log.logger.warning(str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
