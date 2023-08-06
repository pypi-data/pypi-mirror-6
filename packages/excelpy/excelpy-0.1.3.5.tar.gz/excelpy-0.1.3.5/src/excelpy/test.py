#
import shutil
import os
from excelpy import ExcelPy


if __name__ == '__main__':
    try:
        shutil.rmtree('test_slayers')
        os.remove('test_slayers.xlsx')
    except:
        pass
    test_excel = shutil.copyfile('slayers.xlsx', 'test_slayers.xlsx')
    excel = ExcelPy(test_excel)
    excel.deleteSheet('Slayers')
    excel.save()
