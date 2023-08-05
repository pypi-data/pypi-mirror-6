from tailo import Tailo
import unittest

# Create a tailo object to use in the tests
tailo = Tailo()

class TailoStringTest(unittest.TestCase):
    t = { 2: u'\u0301',
          3: u'\u0300',
          5: u'\u0302',
          7: u'\u0304',
          8: u'\u030d' }

    test_strings = ( (u'a', u'a'),
                     (u'a2', u'a'+t[2]),
                     (u'ah', u'ah'),
                     (u'm5', u'm'+t[5]),
                     (u'ah8', u'a'+t[8]+u'h'),
                     (u'pa', u'pa'),
                     (u'Oo7', u'O'+t[7]+u'o'),
                     (u'pa2', u'pa'+t[2]),
                     (u'giam7', u'gia'+t[7]+u'm'),
                     (u'tsing3', u'tsi'+t[3]+u'ng'),
                     (u'ap-tse3-lang5', u'ap-tse'+t[3]+'-la'+t[5]+'ng'),
                     (u'li2 ho2--bo5', u'li'+t[2]+u' ho'+t[2]+u'--bo'+t[5]),
                     (u'bo5 guan5-tsue7 si2-thai',
                         u'bo'+t[5]+u' gua'+t[5]+u'n-tsue'+t[7]+u' si'+t[2]+u'-thai'),
                     (u'bo5 (bu5)', u'bo'+t[5]+' (bu'+t[5]+')'),
                   )

    def test_known_to_num(self):
        """tailo_to_num should give result with numbers in place of tonemarks"""
        for num, mark in self.test_strings:
            result = tailo.to_num(mark)
            self.assertEqual(num, result)

    def test_known_to_mark(self):
        """tailo_to_mark should give result with tonemark diacritics in place of numbers"""
        for num, mark in self.test_strings:
            result = tailo.to_mark(num)
            self.assertEqual(mark, result)

    def test_sanity(self):
        """to_num(to_mark(s))==s for any s"""
        for num, mark in self.test_strings:
            marked = tailo.to_mark(num)
            result = tailo.to_num(mark)
            self.assertEqual(num, result)

class TailoSyllableTest(unittest.TestCase):
    t = { 2: u'\u0301',
          3: u'\u0300',
          5: u'\u0302',
          7: u'\u0304',
          8: u'\u030d' }


    test_syllables = ( (u'a2', u'a'+t[2]),
                       (u'bo3', u'bo'+t[3]),
                       (u'm5', u'm'+t[5]),
                       (u'hak8', u'ha'+t[8]+u'k'),
                       (u'phuann7', u'phua'+t[7]+'nn'),
                     )

    def test_known_mark_syl(self):
        """mark_syl should place one diacritic on a syllable"""
        for syl, mark in self.test_syllables:
            result = tailo.mark_syl(syl)
            self.assertEqual(mark, result)

    def test_mark_syl_not_taiwanese(self):
        """mark_syl should assume it's not Taiwanese for invalid syllables"""
        for s in (u'foo', u'foo-bar'):
            result = tailo.mark_syl(s)
            self.assertEqual(s, result)

    def test_not_a_tone_number(self):
        """mark_syl should assume its not Taiwanese for tone numbers other than 1-9"""
        for s in (u'a0', u'hok10'):
            result = tailo.mark_syl(s)
            self.assertEqual(s, result)

    def test_wrong_tone_number_hptk(self):
        """mark_syl should assume its not Taiwanese if hptk occurs with tone other than none, 4, or 8"""
        for s in (u'ah5', u'hok7'):
            result = tailo.mark_syl(s)
            self.assertEqual(s, result)

class TailoVowelTest(unittest.TestCase):

    known_vowels = ((u'tshiak', u'a'),
                    (u'sueh', u'e'),
                    (u'tng', u'n'),
                    (u'm', u'm'),
                    (u'khiong', u'o'))

    def test_known_vowels(self):
        """should return vowel in order of sonority"""
        for s, v in self.known_vowels:
            result = tailo.marked_vowel(s)
            self.assertEqual(result, v)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
