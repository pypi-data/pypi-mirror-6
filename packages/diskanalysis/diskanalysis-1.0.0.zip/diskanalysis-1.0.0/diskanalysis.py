# -*- coding: cp950 -*-
from diskwalk import diskwalk
import os
'''
This's a module for scaning the specific foder directory,  but It's specific for first layer.
    It need parameter Path initial, and there have two method.
    AnalysisLy1: analysis Dir and return dict.
    WriteInfiles: Write the recode in file, but we should put a parameter in the method is
                  "Path" for decide where outputfile position.
Example:
    ans = diskANA('Y:\digiage')
    recode = ans.AnalysisLy1()
    ans.WriteInfiles('E:\Backup')
'''
class diskanalysis(object):
    def __init__(self, path):
        self.path = path
        self.collect_size = float()
        self.collect_size_dics=dict()
    def AnalysisLy1(self):
        detive =diskwalk(self.path)
        detiveDir=[]
        for i in detive.enumeratedir():
            tmp=os.path.split(i)
            if tmp[0] == self.path:
                tmpD = diskwalk(i)
                for j in tmpD.enumeratepaths():
                    try:
                        self.collect_size += int(os.path.getsize(j))
                    except WindowsError as werr:
                        pass
                self.collect_size = self.collect_size/1024/1024
                self.collect_size_dics[i] = self.collect_size
                self.collect_size = float(0)
        return self.collect_size_dics
    def WriteInfiles(self, path):
        with open(os.path.join(path,'disk_analy.txt'), 'w') as o_wirte:
            for k in self.collect_size_dics:
                o_wirte.write('%s,%s,G\r\n' % (k, int(self.collect_size_dics[k]/1024)))
