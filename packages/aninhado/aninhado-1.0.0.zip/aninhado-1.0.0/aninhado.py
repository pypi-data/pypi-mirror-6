""" Este é o código "aninhado.py", ele fornece uma função chamada
exibir_item_lista() que imprime listas que podem ou não incluir
listas aninhadas. """
def exibir_item_lista(lista):
    
    """ Esta função requer um argumento posicional chamado "lista",
que é qualquer lista Python (de possíveis listas aninhadas). Cada
item de dados na lista fornecida é (recursivamente) impressa na tela
em sua prórpia linha."""
    for item in lista:
        if isinstance(item, list):
            exibir_item_lista(item)
        else:
            print(item)
