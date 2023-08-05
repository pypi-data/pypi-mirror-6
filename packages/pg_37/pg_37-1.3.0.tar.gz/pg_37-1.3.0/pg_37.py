"""
Este é um método para tratamento de listas aninhadas!
"""
def print_lol(alista, edent=False, nivel=0):
    """
    Este método recebe um parametro obrigatório: uma lista aninhada ou não,
    além de dois parametros opcionais: se tem recuo e se tiver recuo, qual
    o espaço de edentação.
    """
    for each in alista:
        if isinstance (each, list):
            print_lol(each, nivel+1)
        else:
            if edent:
                for espaco in range(nivel):
                    print ('\t', end='')
            print (each)
