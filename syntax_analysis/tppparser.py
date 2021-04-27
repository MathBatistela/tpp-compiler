from sys import argv, exit, path

path.append("../")

import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="log-parser.txt",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s",
)
log = logging.getLogger()

import ply.yacc as yacc


from lexical_analysis.tpplexer_module import TppLexer
import ply.lex as lex

tokens = TppLexer.tokens
lexer = TppLexer().build()


class NewLexToken(object):
    def __repr__(self):
        return "*"


lex.LexToken = NewLexToken

from mytree import MyNode
from anytree.exporter import DotExporter, UniqueDotExporter
from anytree import RenderTree, AsciiStyle


def p_programa(p):
    """programa : lista_declaracoes"""

    global root

    programa = MyNode(name="programa", type="PROGRAMA")

    root = programa
    p[0] = programa
    p[1].parent = programa


def p_lista_declaracoes(p):
    """lista_declaracoes : lista_declaracoes declaracao
    | declaracao
    """
    father = MyNode(name="lista_declaracoes", type="LISTA_DECLARACOES")
    p[0] = father
    p[1].parent = father

    if len(p) > 2:
        p[2].parent = father


def p_declaracao(p):
    """declaracao : declaracao_variaveis
    | inicializacao_variaveis
    | declaracao_funcao
    """
    father = MyNode(name="declaracao", type="DECLARACAO")
    p[0] = father
    p[1].parent = father


def p_declaracao_variaveis(p):
    """declaracao_variaveis : tipo DOIS_PONTOS lista_variaveis"""

    father = MyNode(name="declaracao_variaveis", type="DECLARACAO_VARIAVEIS")
    p[0] = father

    p[1].parent = father

    child = MyNode(name="dois_pontos", type="DOIS_PONTOS", parent=father)
    child_sym = MyNode(name=p[2], line=p.lineno(2), type="SIMBOLO", parent=child)
    p[2] = child

    p[3].parent = father


def p_inicializacao_variaveis(p):
    """inicializacao_variaveis : atribuicao"""

    father = MyNode(name="inicializacao_variaveis", type="INICIALIZACAO_VARIAVEIS")
    p[0] = father
    p[1].parent = father


def p_lista_variaveis(p):
    """lista_variaveis : lista_variaveis VIRGULA var
    | var
    """
    father = MyNode(name="lista_variaveis", type="LISTA_VARIAVEIS")
    p[0] = father
    if len(p) > 2:
        p[1].parent = father
        child = MyNode(name="virgula", type="VIRGULA", parent=father)
        child_sym = MyNode(name=",", type="SIMBOLO", parent=child)
        p[3].parent = father
    else:
        p[1].parent = father


def p_var(p):
    """var : ID
    | ID indice
    """

    father = MyNode(name="var", type="VAR")
    p[0] = father
    child = MyNode(name="ID", type="ID", parent=father)
    child_id = MyNode(name=p[1], line=p.lineno(1), type="ID", parent=child)
    p[1] = child
    if len(p) > 2:
        p[2].parent = father


def p_indice(p):
    """indice : indice ABRE_COLCHETE expressao FECHA_COLCHETE
    | ABRE_COLCHETE expressao FECHA_COLCHETE
    """
    father = MyNode(name="indice", type="INDICE")
    p[0] = father
    if len(p) == 5:
        p[1].parent = father

        child2 = MyNode(name="abre_colchete", type="ABRE_COLCHETE", parent=father)
        child_sym2 = MyNode(name=p[2], line=p.lineno(2), type="SIMBOLO", parent=child2)
        p[2] = child2

        p[3].parent = father

        child4 = MyNode(name="fecha_colchete", type="FECHA_COLCHETE", parent=father)
        child_sym4 = MyNode(name=p[4], line=p.lineno(4), type="SIMBOLO", parent=child4)
        p[4] = child4
    else:
        child1 = MyNode(name="abre_colchete", type="ABRE_COLCHETE", parent=father)
        child_sym1 = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child1)
        p[1] = child1

        p[2].parent = father

        child3 = MyNode(name="fecha_colchete", type="FECHA_COLCHETE", parent=father)
        child_sym3 = MyNode(name=p[3], line=p.lineno(3), type="SIMBOLO", parent=child3)
        p[3] = child3


def p_indice_error(p):
    """indice : ABRE_COLCHETE error FECHA_COLCHETE
    | indice ABRE_COLCHETE error FECHA_COLCHETE
    """

    print("\tErro na definicao do indice >>>", end="\t")

    for token in p:
        if token:
            print(token, end="  ")
    print()

    error_line = p.lineno(2)
    father = MyNode(name="ERROR::{}".format(error_line), type="ERROR")
    logging.error("Syntax error parsing index rule at line {}".format(error_line))
    parser.errok()
    p[0] = father


def p_tipo(p):
    """tipo : INTEIRO
    | FLUTUANTE
    """

    father = MyNode(name="tipo", type="TIPO")
    p[0] = father

    if p[1] == "inteiro":
        child1 = MyNode(name="INTEIRO", type="INTEIRO", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type=p[1].upper(), parent=child1)
        p[1] = child1
    else:
        child1 = MyNode(name="FLUTUANTE", type="FLUTUANTE", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type=p[1].upper(), parent=child1)


def p_declaracao_funcao(p):
    """declaracao_funcao : tipo cabecalho
    | cabecalho
    """
    father = MyNode(name="declaracao_funcao", type="DECLARACAO_FUNCAO")
    p[0] = father
    p[1].parent = father

    if len(p) == 3:
        p[2].parent = father


def p_cabecalho(p):
    """cabecalho : ID ABRE_PARENTESE lista_parametros FECHA_PARENTESE corpo FIM"""

    father = MyNode(name="cabecalho", type="CABECALHO")
    p[0] = father

    child1 = MyNode(name="ID", type="ID", parent=father)
    child_id = MyNode(name=p[1], line=p.lineno(1), type="ID", parent=child1)
    p[1] = child1

    child2 = MyNode(name="ABRE_PARENTESE", type="ABRE_PARENTESE", parent=father)
    child_sym2 = MyNode(name="(", type="SIMBOLO", parent=child2)
    p[2] = child2

    p[3].parent = father

    child4 = MyNode(name="FECHA_PARENTESE", type="FECHA_PARENTESE", parent=father)
    child_sym4 = MyNode(name=")", type="SIMBOLO", parent=child4)
    p[4] = child4

    p[5].parent = father

    child6 = MyNode(name="FIM", type="FIM", parent=father)
    child_id = MyNode(name="fim", type="FIM", parent=child6)
    p[6] = child6


def p_cabecalho_error(p):
    """cabecalho : ID ABRE_PARENTESE error FECHA_PARENTESE corpo FIM
    | ID ABRE_PARENTESE lista_parametros FECHA_PARENTESE error FIM
    | error ABRE_PARENTESE lista_parametros FECHA_PARENTESE corpo FIM
    """

    print("\tErro na definição do cabeçalho >>>", end="\t")

    for token in p:
        if token:
            print(token, end="  ")
    print()

    error_line = p.lineno(2)
    father = MyNode(name=f"ERROR::{error_line}", type="ERROR")
    logging.error(f"Syntax error parsing index rule at line {error_line}")
    parser.errok()
    p[0] = father


def p_lista_parametros(p):
    """lista_parametros : lista_parametros VIRGULA parametro
    | parametro
    | vazio
    """

    father = MyNode(name="lista_parametros", type="LISTA_PARAMETROS")
    p[0] = father
    p[1].parent = father

    if len(p) > 2:
        child2 = MyNode(name="virgula", type="VIRGULA", parent=father)
        child_sym2 = MyNode(name=",", type="SIMBOLO", parent=child2)
        p[2] = child2
        p[3].parent = father


def p_parametro(p):
    """parametro : tipo DOIS_PONTOS ID
    | parametro ABRE_COLCHETE FECHA_COLCHETE
    """

    father = MyNode(name="parametro", type="PARAMETRO")
    p[0] = father
    p[1].parent = father

    if p[2] == ":":
        child2 = MyNode(name="dois_pontos", type="DOIS_PONTOS", parent=father)
        child_sym2 = MyNode(name=":", type="SIMBOLO", parent=child2)
        p[2] = child2

        child3 = MyNode(name="id", type="ID", parent=father)
        child_id = MyNode(name=p[3], line=p.lineno(3), type="ID", parent=child3)
    else:
        child2 = MyNode(name="abre_colchete", type="ABRE_COLCHETE", parent=father)
        child_sym2 = MyNode(name="[", type="SIMBOLO", parent=child2)
        p[2] = child2

        child3 = MyNode(name="fecha_colchete", type="FECHA_COLCHETE", parent=father)
        child_sym3 = MyNode(name="]", type="SIMBOLO", parent=child3)
        p[3] = child3


def p_parametro_error(p):
    """parametro : tipo error ID
    | error ID
    | parametro error FECHA_COLCHETE
    | parametro ABRE_COLCHETE error
    """

    print("\tErro na definição do parâmetro >>>", end="\t")

    for token in p:
        if token:
            print(token, end="  ")
    print()

    error_line = p.lineno(2)
    father = MyNode(name=f"ERROR::{error_line}", type="ERROR")
    logging.error(f"Syntax error parsing index rule at line {error_line}")
    parser.errok()
    p[0] = father


def p_corpo(p):
    """corpo : corpo acao
    | vazio
    """

    father = MyNode(name="corpo", type="CORPO")
    p[0] = father
    p[1].parent = father

    if len(p) > 2:
        p[2].parent = father


def p_acao(p):
    """acao : expressao
    | declaracao_variaveis
    | se
    | repita
    | leia
    | escreva
    | retorna
    """

    father = MyNode(name="acao", type="ACAO")
    p[0] = father
    p[1].parent = father


def p_se(p):
    """se : SE expressao ENTAO corpo FIM
    | SE expressao ENTAO corpo SENAO corpo FIM
    """

    father = MyNode(name="se", type="SE")
    p[0] = father

    child1 = MyNode(name="SE", type="SE", parent=father)
    child_se = MyNode(name=p[1], line=p.lineno(1), type="SE", parent=child1)
    p[1] = child1

    p[2].parent = father

    child3 = MyNode(name="ENTAO", type="ENTAO", parent=father)
    child_entao = MyNode(name=p[3], line=p.lineno(3), type="ENTAO", parent=child3)
    p[3] = child3

    p[4].parent = father

    if len(p) == 8:
        child5 = MyNode(name="SENAO", type="SENAO", parent=father)
        child_senao = MyNode(name=p[5], line=p.lineno(5), type="SENAO", parent=child5)
        p[5] = child5

        p[6].parent = father

        child7 = MyNode(name="FIM", type="FIM", parent=father)
        child_fim = MyNode(name=p[7], line=p.lineno(7), type="FIM", parent=child7)
        p[7] = child7
    else:
        child5 = MyNode(name="fim", type="FIM", parent=father)
        child_fim = MyNode(name=p[5], line=p.lineno(5), type="FIM", parent=child5)
        p[5] = child5


def p_se_error(p):
    """se : error expressao ENTAO corpo FIM
    | SE expressao error corpo FIM
    | error expressao ENTAO corpo SENAO corpo FIM
    | SE expressao error corpo SENAO corpo FIM
    | SE expressao ENTAO corpo error corpo FIM
    | SE expressao ENTAO corpo SENAO corpo
    """

    print("\tErro na definição/condição 'SE' >>>", end="\t")

    for token in p:
        if token:
            print(token, end="  ")
    print()

    error_line = p.lineno(2)
    father = MyNode(name=f"ERROR::{error_line}", type="ERROR")
    logging.error(f"Syntax error parsing index rule at line {error_line}")
    parser.errok()
    p[0] = father


def p_repita(p):
    """repita : REPITA corpo ATE expressao"""

    father = MyNode(name="repita", type="REPITA")
    p[0] = father

    child1 = MyNode(name="REPITA", type="REPITA", parent=father)
    child_repita = MyNode(name=p[1], line=p.lineno(1), type="REPITA", parent=child1)
    p[1] = child1

    p[2].parent = father

    child3 = MyNode(name="ATE", type="ATE", parent=father)
    child_ate = MyNode(name=p[3], line=p.lineno(3), type="ATE", parent=child3)
    p[3] = child3

    p[4].parent = father


def p_repita_error(p):
    """repita : error corpo ATE expressao
    | REPITA corpo error expressao
    """

    print("\tErro na definição/condição 'REPITA' >>>", end="\t")

    for token in p:
        if token:
            print(token, end="  ")
    print()

    error_line = p.lineno(2)
    father = MyNode(name=f"ERROR::{error_line}", type="ERROR")
    logging.error(f"Syntax error parsing index rule at line {error_line}")
    parser.errok()
    p[0] = father


def p_atribuicao(p):
    """atribuicao : var ATRIBUICAO expressao"""

    father = MyNode(name="atribuicao", type="ATRIBUICAO")
    p[0] = father

    p[1].parent = father

    child2 = MyNode(name="ATRIBUICAO", type="ATRIBUICAO", parent=father)
    child_sym2 = MyNode(name=":=", type="SIMBOLO", parent=child2)
    p[2] = child2

    p[3].parent = father


def p_leia(p):
    """leia : LEIA ABRE_PARENTESE var FECHA_PARENTESE"""

    father = MyNode(name="leia", type="LEIA")
    p[0] = father

    child1 = MyNode(name="LEIA", type="LEIA", parent=father)
    child_sym1 = MyNode(name=p[1], line=p.lineno(1), type="LEIA", parent=child1)
    p[1] = child1

    child2 = MyNode(name="ABRE_PARENTESE", type="ABRE_PARENTESE", parent=father)
    child_sym2 = MyNode(name="(", type="SIMBOLO", parent=child2)
    p[2] = child2

    p[3].parent = father

    child4 = MyNode(name="FECHA_PARENTESE", type="FECHA_PARENTESE", parent=father)
    child_sym4 = MyNode(name=")", type="SIMBOLO", parent=child4)
    p[4] = child4


def p_leia_error(p):
    """leia : LEIA ABRE_PARENTESE error FECHA_PARENTESE"""

    print("\tErro na definicao da expressão 'LEIA' >>>", end="\t")

    for token in p:
        if token:
            print(token, end="  ")
    print()

    error_line = p.lineno(2)
    father = MyNode(name=f"ERROR::{error_line}", type="ERROR")
    logging.error(f"Syntax error parsing index rule at line {error_line}")
    parser.errok()
    p[0] = father


def p_escreva(p):
    """escreva : ESCREVA ABRE_PARENTESE expressao FECHA_PARENTESE"""

    father = MyNode(name="escreva", type="ESCREVA")
    p[0] = father

    child1 = MyNode(name="ESCREVA", type="ESCREVA", parent=father)
    child_sym1 = MyNode(name=p[1], line=p.lineno(1), type="ESCREVA", parent=child1)
    p[1] = child1

    child2 = MyNode(name="ABRE_PARENTESE", type="ABRE_PARENTESE", parent=father)
    child_sym2 = MyNode(name="(", type="SIMBOLO", parent=child2)
    p[2] = child2

    p[3].parent = father

    child4 = MyNode(name="FECHA_PARENTESE", type="FECHA_PARENTESE", parent=father)
    child_sym4 = MyNode(name=")", type="SIMBOLO", parent=child4)
    p[4] = child4


def p_retorna(p):
    """retorna : RETORNA ABRE_PARENTESE expressao FECHA_PARENTESE"""

    father = MyNode(name="retorna", type="RETORNA")
    p[0] = father

    child1 = MyNode(name="RETORNA", type="RETORNA", parent=father)
    child_sym1 = MyNode(name=p[1], line=p.lineno(1), type="RETORNA", parent=child1)
    p[1] = child1

    child2 = MyNode(name="ABRE_PARENTESE", type="ABRE_PARENTESE", parent=father)
    child_sym2 = MyNode(name="(", type="SIMBOLO", parent=child2)
    p[2] = child2

    p[3].parent = father

    child4 = MyNode(name="FECHA_PARENTESE", type="FECHA_PARENTESE", parent=father)
    child_sym4 = MyNode(name=")", type="SIMBOLO", parent=child4)
    p[4] = child4


def p_expressao(p):
    """expressao : expressao_logica
    | atribuicao
    """

    father = MyNode(name="expressao", type="EXPRESSAO")
    p[0] = father
    p[1].parent = father


def p_expressao_logica(p):
    """expressao_logica : expressao_simples
    | expressao_logica operador_logico expressao_simples
    """

    father = MyNode(name="expressao_logica", type="EXPRESSAO_LOGICA")
    p[0] = father
    p[1].parent = father

    if len(p) > 2:
        p[2].parent = father
        p[3].parent = father


def p_expressao_simples(p):
    """expressao_simples : expressao_aditiva
    | expressao_simples operador_relacional expressao_aditiva
    """

    father = MyNode(name="expressao_simples", type="EXPRESSAO_SIMPLES")
    p[0] = father
    p[1].parent = father

    if len(p) > 2:
        p[2].parent = father
        p[3].parent = father


def p_expressao_aditiva(p):
    """expressao_aditiva : expressao_multiplicativa
    | expressao_aditiva operador_soma expressao_multiplicativa
    """

    father = MyNode(name="expressao_aditiva", type="EXPRESSAO_ADITIVA")
    p[0] = father
    p[1].parent = father

    if len(p) > 2:
        p[2].parent = father
        p[3].parent = father


def p_expressao_multiplicativa(p):
    """expressao_multiplicativa : expressao_unaria
    | expressao_multiplicativa operador_multiplicacao expressao_unaria
    """

    father = MyNode(name="expressao_multiplicativa", type="EXPRESSAO_MULTIPLICATIVA")
    p[0] = father
    p[1].parent = father

    if len(p) > 2:
        p[2].parent = father
        p[3].parent = father


def p_expressao_unaria(p):
    """expressao_unaria : fator
    | operador_soma fator
    | operador_negacao fator
    """

    father = MyNode(name="expressao_unaria", type="EXPRESSAO_UNARIA")
    p[0] = father
    p[1].parent = father

    if p[1] == "!":
        child1 = MyNode(name="operador_negacao", type="OPERADOR_NEGACAO", parent=father)
        child_sym1 = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child1)
        p[1] = child1
    else:
        p[1].parent = father

    if len(p) > 2:
        p[2].parent = father


def p_operador_relacional(p):
    """operador_relacional : MENOR
    | MAIOR
    | IGUAL
    | DIFERENTE
    | MENOR_IGUAL
    | MAIOR_IGUAL
    """

    father = MyNode(name="operador_relacional", type="OPERADOR_RELACIONAL")
    p[0] = father

    if p[1] == "<":
        child = MyNode(name="MENOR", type="MENOR", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
    elif p[1] == ">":
        child = MyNode(name="MAIOR", type="MAIOR", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
    elif p[1] == "=":
        child = MyNode(name="IGUAL", type="IGUAL", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
    elif p[1] == "<>":
        child = MyNode(name="DIFERENTE", type="DIFERENTE", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
    elif p[1] == "<=":
        child = MyNode(name="MENOR_IGUAL", type="MENOR_IGUAL", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
    elif p[1] == ">=":
        child = MyNode(name="MAIOR_IGUAL", type="MAIOR_IGUAL", parent=father)
        child_sym = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
    else:
        print("Erro operador relacional")

    p[1] = child


def p_operador_soma(p):
    """operador_soma : MAIS
    | MENOS
    """

    if p[1] == "+":
        mais = MyNode(name="MAIS", type="MAIS")
        mais_lexema = MyNode(name="+", type="SIMBOLO", parent=mais)
        p[0] = MyNode(name="operador_soma", type="OPERADOR_SOMA", children=[mais])
    else:
        menos = MyNode(name="MENOS", type="MENOS")
        menos_lexema = MyNode(name="-", type="SIMBOLO", parent=menos)
        p[0] = MyNode(name="operador_soma", type="OPERADOR_SOMA", children=[menos])


def p_operador_logico(p):
    """operador_logico : E
    | OU
    """

    if p[1] == "&&":
        child = MyNode(name="E", type="E")
        child_lexema = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
        p[0] = MyNode(name="operador_logico", type="OPERADOR_LOGICO", children=[child])
    else:
        child = MyNode(name="OU", type="OU")
        child_lexema = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
        p[0] = MyNode(name="operador_logico", type="OPERADOR_SOMA", children=[child])


def p_operador_negacao(p):
    """operador_negacao : NAO"""

    if p[1] == "!":
        child = MyNode(name="NAO", type="NAO")
        negacao_lexema = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
        p[0] = MyNode(
            name="operador_negacao", type="OPERADOR_NEGACAO", children=[child]
        )


def p_operador_multiplicacao(p):
    """operador_multiplicacao : VEZES
    | DIVIDE
    """

    if p[1] == "*":
        child = MyNode(name="VEZES", type="VEZES")
        vezes_lexema = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child)
        p[0] = MyNode(
            name="operador_multiplicacao",
            type="OPERADOR_MULTIPLICACAO",
            children=[child],
        )
    else:
        divide = MyNode(name="DIVIDE", type="DIVIDE")
        divide_lexema = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=divide)
        p[0] = MyNode(
            name="operador_multiplicacao",
            type="OPERADOR_MULTIPLICACAO",
            children=[divide],
        )


def p_fator(p):
    """fator : ABRE_PARENTESE expressao FECHA_PARENTESE
    | var
    | chamada_funcao
    | numero
    """

    father = MyNode(name="fator", type="FATOR")
    p[0] = father

    if len(p) > 2:
        child1 = MyNode(name="ABRE_PARENTESE", type="ABRE_PARENTESE", parent=father)
        child_sym1 = MyNode(name=p[1], line=p.lineno(1), type="SIMBOLO", parent=child1)
        p[1] = child1

        p[2].parent = father

        child3 = MyNode(name="FECHA_PARENTESE", type="FECHA_PARENTESE", parent=father)
        child_sym3 = MyNode(name=p[3], line=p.lineno(3), type="SIMBOLO", parent=child3)
        p[3] = child3
    else:
        p[1].parent = father


def p_fator_error(p):
    """fator : ABRE_PARENTESE error FECHA_PARENTESE"""

    print("\tErro na definião do fator >>>", end="\t")

    for token in p:
        if token:
            print(token, end="  ")
    print()

    error_line = p.lineno(2)
    father = MyNode(name=f"ERROR::{error_line}", type="ERROR")
    logging.error(f"Syntax error parsing index rule at line {error_line}")
    parser.errok()
    p[0] = father


def p_numero(p):
    """numero : NUM_INTEIRO
    | NUM_PONTO_FLUTUANTE
    | NUM_NOTACAO_CIENTIFICA
    """

    father = MyNode(name="numero", type="NUMERO")
    p[0] = father

    if str(p[1]).find(".") == -1:
        aux = MyNode(name="NUM_INTEIRO", type="NUM_INTEIRO", parent=father)
        aux_val = MyNode(name=p[1], line=p.lineno(1), type="VALOR", parent=aux)
        p[1] = aux
    elif str(p[1]).find("e") >= 0:
        aux = MyNode(
            name="NUM_NOTACAO_CIENTIFICA", type="NUM_NOTACAO_CIENTIFICA", parent=father
        )
        aux_val = MyNode(name=p[1], line=p.lineno(1), type="VALOR", parent=aux)
        p[1] = aux
    else:
        aux = MyNode(
            name="NUM_PONTO_FLUTUANTE", type="NUM_PONTO_FLUTUANTE", parent=father
        )
        aux_val = MyNode(name=p[1], line=p.lineno(1), type="VALOR", parent=aux)
        p[1] = aux


def p_chamada_funcao(p):
    """chamada_funcao : ID ABRE_PARENTESE lista_argumentos FECHA_PARENTESE"""

    father = MyNode(name="chamada_funcao", type="CHAMADA_FUNCAO")
    p[0] = father
    if len(p) > 2:
        child1 = MyNode(name="ID", type="ID", parent=father)
        child_id = MyNode(name=p[1], line=p.lineno(1), type="ID", parent=child1)
        p[1] = child1

        child2 = MyNode(name="ABRE_PARENTESE", type="ABRE_PARENTESE", parent=father)
        child_sym = MyNode(name=p[2], line=p.lineno(2), type="SIMBOLO", parent=child2)
        p[2] = child2

        p[3].parent = father

        child4 = MyNode(name="FECHA_PARENTESE", type="FECHA_PARENTESE", parent=father)
        child_sym = MyNode(name=p[4], line=p.lineno(4), type="SIMBOLO", parent=child4)
        p[4] = child4
    else:
        p[1].parent = father


def p_lista_argumentos(p):
    """lista_argumentos : lista_argumentos VIRGULA expressao
    | expressao
    | vazio
    """

    father = MyNode(name="lista_argumentos", type="LISTA_ARGUMENTOS")
    p[0] = father

    if len(p) > 2:
        p[1].parent = father

        child2 = MyNode(name="VIRGULA", type="VIRGULA", parent=father)
        child_sym = MyNode(name=p[2], line=p.lineno(2), type="SIMBOLO", parent=child2)
        p[2] = child2

        p[3].parent = father
    else:
        p[1].parent = father


def p_vazio(p):
    """vazio : """

    father = MyNode(name="vazio", type="VAZIO")
    p[0] = father


def p_error(p):

    if p:
        token = p
        print(
            "Erro:[{line},{column}]: Próximo ao token '{token}'".format(
                line=token.lineno, column=token.lineno, token=token.value
            )
        )

def get_root(file_data):
    parser.parse(file_data)
    global root
    return root
    
def main():
    print()
    aux = argv[1].split(".")
    if aux[-1] != "tpp":
        raise IOError("Not a .tpp file!")
    data = open(argv[1])

    source_file = data.read()
    parser.parse(source_file)

    try:
        if root and root.children != ():
            print("\n-------------OK--------------")
            print("Generating Syntax Tree Graph...")
            DotExporter(root).to_picture(argv[1] + ".ast.png")
            UniqueDotExporter(root).to_picture(argv[1] + ".unique.ast.png")
            DotExporter(root).to_dotfile(argv[1] + ".ast.dot")
            UniqueDotExporter(root).to_dotfile(argv[1] + ".unique.ast.dot")
            print(RenderTree(root, style=AsciiStyle()).by_attr())
            print("Graph was generated.\nOutput file: " + argv[1] + ".ast.png")

            DotExporter(
                root,
                graph="graph",
                nodenamefunc=MyNode.nodenamefunc,
                nodeattrfunc=lambda node: "label=%s" % (node.type),
                edgeattrfunc=MyNode.edgeattrfunc,
                edgetypefunc=MyNode.edgetypefunc,
            ).to_picture(argv[1] + ".ast2.png")

            DotExporter(root, nodenamefunc=lambda node: node.label).to_picture(
                argv[1] + ".ast3.png"
            )

    except NameError:
        print("Não foi possível gerar a árvore sintática.")
    print("\n\n")


parser = yacc.yacc(
    method="LALR",
    optimize=True,
    start="programa",
    debug=True,
    debuglog=log,
    write_tables=False,
    tabmodule="tpp_parser_tab",
)

if __name__ == "__main__":
    main()
