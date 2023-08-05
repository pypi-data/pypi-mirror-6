import unicodedata
import re

class Tailo:
    """"A class for manipulating Tailo pinyin"""
    syllables = (
        u'a', u'ah', u'ai', u'ainn', u'ak', u'am', u'an',
        u'ann', u'ang', u'ap', u'at', u'au', u'ba', u'bah',
        u'bai', u'bak', u'ban', u'bang', u'bat', u'bau', u'be',
        u'beh', u'bik', u'bing', u'bi', u'bian', u'biat', u'biau',
        u'bih', u'bin', u'bio', u'bit', u'biu', u'bo', u'boo', u'bua',
        u'buah', u'buan', u'buat', u'bue', u'bueh', u'bok', u'bong',
        u'bu', u'bui', u'bun', u'but', u'tsa', u'tsah', u'tsai',
        u'tsainn', u'tsak', u'tsam', u'tsan', u'tsann', u'tsang', u'tsap',
        u'tsat', u'tsau', u'tse', u'tseh', u'tsik', u'tsenn', u'tsing',
        u'tsha', u'tshah', u'tshai', u'tshak', u'tsham', u'tshan',
        u'tshann', u'tshang', u'tshap', u'tshat', u'tshau', u'tshauh',
        u'tshe', u'tsheh', u'tshik', u'tshenn', u'tshing', u'tshi',
        u'tshia', u'tshiah', u'tshiak', u'tshiam', u'tshian', u'tshiann',
        u'tshiang', u'tshiap', u'tshiat', u'tshiau', u'tshih', u'tshim',
        u'tshin', u'tshinn', u'tshio', u'tshioh', u'tshiok', u'tshiong',
        u'tship', u'tshit', u'tshiu', u'tshiunn', u'tshng', u'tshngh',
        u'tsho', u'tshoo', u'tshua', u'tshuah', u'tshuan', u'tshuann',
        u'tshuang', u'tshue', u'tshoh', u'tshok', u'tshong', u'tshu',
        u'tshuh', u'tshui', u'tshun', u'tshut', u'tsi', u'tsia', u'tsiah',
        u'tsiam', u'tsian', u'tsiann', u'tsiang', u'tsiap', u'tsiat',
        u'tsiau', u'tsih', u'tsim', u'tsin', u'tsinn', u'tsio', u'tsioh',
        u'tsiok', u'tsiong', u'tsip', u'tsit', u'tsiu', u'tsiunn', u'tsng',
        u'tso', u'tsoo', u'tsua', u'tsuah', u'tsuainn', u'tsuan', u'tsuann',
        u'tsuat', u'tsue', u'tsoh', u'tsok', u'tsong', u'tsu', u'tsuh',
        u'tsui', u'tsun', u'tsut', u'e', u'eh', u'ik', u'enn', u'ing',
        u'ga', u'gai', u'gak', u'gam', u'gan', u'gang', u'gau', u'ge',
        u'gik', u'ging', u'gi', u'gia', u'giah', u'giam', u'gian', u'giang',
        u'giap', u'giat', u'giau', u'gim', u'gin', u'gio', u'gioh', u'giok',
        u'giong', u'giu', u'go', u'goo', u'gua', u'guan', u'guat', u'gue',
        u'gueh', u'gok', u'gong', u'gu', u'gui', u'ha', u'hah', u'hannh',
        u'hai', u'hainn', u'hak', u'ham', u'han', u'hann', u'hang', u'hap',
        u'hat', u'hau', u'he', u'heh', u'hennh', u'hik', u'henn', u'hing',
        u'hi', u'hia', u'hiah', u'hiannh', u'hiam', u'hian', u'hiann',
        u'hiang', u'hiap', u'hiat', u'hiau', u'hiauh', u'him', u'hin',
        u'hinn', u'hio', u'hioh', u'hiok', u'hiong', u'hip', u'hit', u'hiu',
        u'hiunnh', u'hiunn', u'hm', u'hmh', u'hng', u'hngh', u'ho', u'hoo',
        u'hua', u'huah', u'huai', u'huainn', u'huan', u'huann', u'huat', u'hue',
        u'hueh', u'hoh', u'honnh', u'hok', u'honn', u'hong', u'hu', u'hui',
        u'hun', u'hut', u'i', u'ia', u'iah', u'iam', u'ian', u'iann', u'iang',
        u'iap', u'iat', u'iau', u'iaunn', u'im', u'in', u'inn', u'io', u'ioh',
        u'iok', u'iong', u'ip', u'it', u'iu', u'iunn', u'ji', u'jia', u'jiam',
        u'jian', u'jiang', u'jiap', u'jiat', u'jiau', u'jim', u'jin', u'jio',
        u'jiok', u'jiong', u'jip', u'jit', u'jiu', u'juah', u'jue', u'ju',
        u'jun', u'ka', u'kah', u'kai', u'kainn', u'kak', u'kam', u'kan',
        u'kann', u'kang', u'kap', u'kat', u'kau', u'kauh', u'ke', u'keh',
        u'kik', u'kenn', u'king', u'kha', u'khah', u'khai', u'khainn', u'khak',
        u'kham', u'khan', u'khann', u'khang', u'khap', u'khat', u'khau',
        u'khe', u'kheh', u'khennh', u'khik', u'khenn', u'khing', u'khi',
        u'khia', u'khiah', u'khiak', u'khiam', u'khian', u'khiang', u'khiap',
        u'khiat', u'khiau', u'khiauh', u'khih', u'khim', u'khin', u'khinn',
        u'khio', u'khioh', u'khiok', u'khiong', u'khip', u'khit', u'khiu',
        u'khiunn', u'khng', u'kho', u'khoo', u'khua', u'khuah', u'khuai',
        u'khuan', u'khuann', u'khuat', u'khue', u'khueh', u'khok', u'khong',
        u'khu', u'khuh', u'khui', u'khun', u'khut', u'ki', u'kia', u'kiah',
        u'kiam', u'kian', u'kiann', u'kiap', u'kiat', u'kiau', u'kim', u'kin',
        u'kinn', u'kio', u'kioh', u'kiok', u'kiong', u'kip', u'kit', u'kiu',
        u'kiunn', u'kng', u'ko', u'koo', u'kua', u'kuah', u'kuai', u'kuainn',
        u'kuan', u'kuann', u'kuat', u'kue', u'kueh', u'koh', u'kok', u'konn',
        u'kong', u'ku', u'kui', u'kun', u'kut', u'la', u'lah', u'lai', u'lak',
        u'lam', u'lan', u'lang', u'lap', u'lat', u'lau', u'lauh', u'le', u'leh',
        u'lik', u'ling', u'li', u'liah', u'liam', u'lian', u'liang', u'liap',
        u'liat', u'liau', u'lih', u'lim', u'lin', u'lio', u'lioh', u'liok',
        u'liong', u'lip', u'liu', u'lo', u'loo', u'lua', u'luah', u'luan',
        u'luat', u'lue', u'loh', u'lok', u'long', u'lu', u'lui', u'lun', u'lut',
        u'm', u'ma', u'mai', u'mau', u'mauh', u'me', u'meh', u'mi', u'mia',
        u'miau', u'mih', u'mng', u'moo', u'mua', u'mooh', u'mui', u'na', u'nah',
        u'nai', u'nau', u'nauh', u'ne', u'neh', u'ng', u'nga', u'ngai', u'ngau',
        u'nge', u'ngeh', u'ngia', u'ngiau', u'ngiauh', u'ngoo', u'ni', u'nia',
        u'niau', u'nih', u'niu', u'nng', u'noo', u'nua', u'o', u'oo', u'ua',
        u'uah', u'uai', u'uainn', u'uan', u'uann', u'uang', u'uat', u'ue',
        u'ueh', u'oh', u'ok', u'om', u'onn', u'ong', u'pa', u'pah', u'pai',
        u'pak', u'pan', u'pang', u'pat', u'pau', u'pe', u'peh', u'pik', u'penn',
        u'ping', u'pha', u'phah', u'phai', u'phainn', u'phak', u'phan', u'phann',
        u'phang', u'phau', u'phauh', u'phe', u'phik', u'phenn', u'phing', u'phi',
        u'phiah', u'phiak', u'phian', u'phiann', u'phiang', u'phiat', u'phiau',
        u'phih', u'phin', u'phinn', u'phio', u'phit', u'phngh', u'pho', u'phoo',
        u'phua', u'phuah', u'phuan', u'phuann', u'phuat', u'phue', u'phueh',
        u'phoh', u'phok', u'phong', u'phu', u'phuh', u'phui', u'phun', u'phut',
        u'pi', u'piah', u'piak', u'pian', u'piann', u'piang', u'piat', u'piau',
        u'pih', u'pin', u'pinn', u'pio', u'pit', u'piu', u'png', u'po', u'poo',
        u'pua', u'puah', u'puan', u'puann', u'puat', u'pue', u'pueh', u'poh',
        u'pok', u'pong', u'pu', u'puh', u'pui', u'pun', u'put', u'sa', u'sah',
        u'sannh', u'sai', u'sak', u'sam', u'san', u'sann', u'sang', u'sap',
        u'sat', u'sau', u'se', u'seh', u'sik', u'senn', u'sing', u'si', u'sia',
        u'siah', u'siak', u'siam', u'sian', u'siann', u'siang', u'siap', u'siat',
        u'siau', u'sih', u'sim', u'sin', u'sinn', u'sio', u'sioh', u'siok',
        u'siong', u'sip', u'sit', u'siu', u'siunn', u'sng', u'sngh', u'so',
        u'soo', u'sua', u'suah', u'suai', u'suainn', u'suan', u'suann', u'suat',
        u'sue', u'sueh', u'soh', u'sok', u'som', u'song', u'su', u'suh', u'sui',
        u'sun', u'sut', u'ta', u'tah', u'tai', u'tainn', u'tak', u'tam', u'tan',
        u'tann', u'tang', u'tap', u'tat', u'tau', u'tauh', u'te', u'teh', u'tik',
        u'tenn', u'ting', u'tha', u'thah', u'thai', u'thak', u'tham', u'than',
        u'thann', u'thang', u'thap', u'that', u'thau', u'the', u'theh', u'thik',
        u'thenn', u'thing', u'thi', u'thiah', u'thiam', u'thian', u'thiann',
        u'thiap', u'thiat', u'thiau', u'thih', u'thim', u'thin', u'thinn', u'thio',
        u'thiok', u'thiong', u'thiu', u'thng', u'tho', u'thoo', u'thua', u'thuah',
        u'thuan', u'thuann', u'thuat', u'thoh', u'thok', u'thong', u'thu', u'thuh',
        u'thui', u'thun', u'thut', u'ti', u'tia', u'tiah', u'tiak', u'tiam', u'tian',
        u'tiann', u'tiap', u'tiat', u'tiau', u'tih', u'tinnh', u'tim', u'tin',
        u'tinn', u'tio', u'tioh', u'tiok', u'tiong', u'tit', u'tiu', u'tiuh',
        u'tiunn', u'tng', u'to', u'too', u'tua', u'tuan', u'tuann', u'tuat', u'tue',
        u'toh', u'tok', u'tom', u'tong', u'tu', u'tuh', u'tui', u'tun', u'tut', u'u',
        u'uh', u'ui', u'un', u'ut'
    )

    tones = { u'2': u'\u0301',
              u'3': u'\u0300',
              u'5': u'\u0302',
              u'7': u'\u0304',
              u'8': u'\u030d' }

    # these are the tailo markable vowels in order of sonority
    vowels = (u'a', u'A', u'oo', u'Oo', u'OO', u'e', u'E',
              u'o', u'O', u'i', u'I', u'u', u'U', u'n', u'N', u'm', u'M')
    
    # these final consonants are compatible with 8th tone only
    hptk = (u'h', u'p', u't', u'k',
            u'H', u'P', u'T', u'K')

    # regex pattern for tailo words in a string
    pattern = re.compile(u"([A-Za-z]{1,7}[23578]{0,1})([^A-Za-z0-9]|$)")

    numpattern = re.compile(u'([A-Za-z]{1,7})([\u0301\u0300\u0302\u0304\u030d])([A-Za-z]{0,6})([^A-Za-z]|$)')

    def to_num(self, string):
        """to_num converts a u'str' with tone diacritics to a string with tone numbers"""
        return re.sub(self.numpattern, self.to_num_matcher, string)

    def to_num_matcher(self, mobj):
        """for a match object of the form numpattern, replace the tone diacritic by a number"""
        group = mobj.group(0, 1, 2, 3, 4)
        num = u''
        for t in self.tones:
            if group[2]==self.tones[t]: num=t
        return group[1]+group[3]+num+group[4]

    def to_mark(self, string):
        """to_mark converts a u'str' with tone numbers to a string with diacritics"""
        return re.sub(self.pattern, self.mark_syl, string)

    def mark_syl(self, syl):
        """mark_syl marks the tone on one syllable with the appropriate diacritic"""
        # get a match object as string
        if type(syl) <> unicode:
            after = syl.group(2)
            rsyl = syl.group(0) #save the original string
            syl = syl.group(1)
        else:
            after = u''
            rsyl = syl

        # the tone is the last number in the word
        # the word is the string minus the tone number
        # f is the final character in the hptk check
        t = syl[len(syl)-1]
        w = syl[0:len(syl)-1]
        f = u''
        if len(w) >1: f = w[len(w)-1]

        # invalid tone or word, do nothing, hptk check fails, do nothing
        if t not in self.tones or w.lower() not in self.syllables: return rsyl
        elif f in self.hptk and t != u'8': return rsyl
        elif f not in self.hptk and t == u'8': return rsyl

        #if it was from a regex match, put the match trailing group back in
        w+=after

        # decide which character gets the mark
        v = self.marked_vowel(w)

        # replace the character with itself plus the proper tone mark
        if v == u'oo': #special case for oo
            return w.replace(v, u'o'+self.tones[t]+u'o')
        elif v == u'Oo':
            return w.replace(v, u'O'+self.tones[t]+u'o')
        elif v == u'OO':
            return w.replace(v, u'O'+self.tones[t]+u'O')
        else:
            return w.replace(v, v+self.tones[t])

    def marked_vowel(self, syl):
        """marked_vowel returns the highest sonority vowel"""
        for v in self.vowels:
            if syl.find(v) >= 0:
                return v
