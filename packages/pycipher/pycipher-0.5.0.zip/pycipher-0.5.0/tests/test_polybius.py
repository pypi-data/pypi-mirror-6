from pycipher import PolybiusSquare
import unittest

class TestPolybius(unittest.TestCase):

    def test_encipher(self):
        keys = (('phqgiumeaylnofdxkrcvstzwb',5,'ABCDE'),
                ('uqfigkydlvmznxephrswaotcb',5,'BCDEF'))
        plaintext = ('abcdefghiiklmnopqrstuvwxyzabcdefghiiklmnopqrstuvwxyz',
                     'abcdefghiiklmnopqrstuvwxyzabcdefghiiklmnopqrstuvwxyz')
        ciphertext = ('BDEEDDCEBCCDADABAEAEDBCABBCBCCAAACDCEAEBBADEEDDABEECBDEEDDCEBCCDADABAEAEDBCABBCBCCAAACDCEAEBBADEEDDABEEC',
                      'FBFFFECDDFBDBFECBEBECBCEDBDDFCEBBCEDEEFDBBCFEFDECCDCFBFFFECDDFBDBFECBEBECBCEDBDDFCEBBCEDEEFDBBCFEFDECCDC')
        for i,key in enumerate(keys):
            enc = PolybiusSquare(*key).encipher(plaintext[i])
            self.assertEqual(enc.upper(), ciphertext[i].upper())

    def test_decipher(self):
        keys = (('phqgiumeaylnofdxkrcvstzwb',5,'ABCDE'),
                ('uqfigkydlvmznxephrswaotcb',5,'BCDEF'))
        plaintext= ('abcdefghiiklmnopqrstuvwxyzabcdefghiiklmnopqrstuvwxyz',
                    'abcdefghiiklmnopqrstuvwxyzabcdefghiiklmnopqrstuvwxyz')
        ciphertext = ('BDEEDDCEBCCDADABAEAEDBCABBCBCCAAACDCEAEBBADEEDDABEECBDEEDDCEBCCDADABAEAEDBCABBCBCCAAACDCEAEBBADEEDDABEEC',
                      'FBFFFECDDFBDBFECBEBECBCEDBDDFCEBBCEDEEFDBBCFEFDECCDCFBFFFECDDFBDBFECBEBECBCEDBDDFCEBBCEDEEFDBBCFEFDECCDC')
        for i,key in enumerate(keys):
            dec = PolybiusSquare(*key).decipher(ciphertext[i])
            self.assertEqual(dec.upper(), plaintext[i].upper())
            	
if __name__ == '__main__':
    unittest.main()
