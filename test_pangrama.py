# coding:utf-8
import unittest
import string

def verificar_pangrama(frase):
    for letra in string.ascii_lowercase:
        if letra not in frase.lower():
            return False

    return True


class VerificarPangramaTests(unittest.TestCase):
    def test_metodo_de_teste(self):
        pass

    def test_retorna_verdadeiro_quando_frase_pangrama(self):
        # Arrange
        frase = "Zebras caolhas de Java querem mandar fax para moça gigante de New York"

        # Act
        frase_eh_pangrama = verificar_pangrama(frase)

        # Assert

        self.assertTrue(frase_eh_pangrama)