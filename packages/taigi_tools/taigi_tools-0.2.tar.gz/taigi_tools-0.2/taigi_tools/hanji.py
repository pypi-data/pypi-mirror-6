import codecs
import re

class Hanji:
    DATFILE = 'TLHJ.DAT'
    def __init__(self):
        self.conversion_table = []
        with codecs.open(self.DATFILE, 'r', 'utf-8') as f:
            for l in sorted(f, key=len, reverse=True):
                self.conversion_table.append(l.rstrip().split('\t'))

    hanjipattern = re.compile(u"([^A-Za-z0-9]|^)([A-Za-z]{1,7}[23578]{0,1}[-]{0,2})+")

    def to_hanjipattern(self, mobj):
        s = mobj.group(0).lower()
        for x in self.conversion_table:
            s = s.replace(x[0], x[1])
        return s

    def to_hanji(self, string):
        string = re.sub(self.hanjipattern, self.to_hanjipattern, string)
        return string.replace(' ', '')
    
    def to_tailo(self, string):
        for x in self.conversion_table:
            string = string.replace(x[1], x[0]+' ')
        return string
