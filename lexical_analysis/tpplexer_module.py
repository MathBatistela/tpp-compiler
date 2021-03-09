import ply.lex as lex

class TppLexer(object):
    
    # Lista de tokens
    
    tokens = [
    "ID",  # identificador
    # numerais
    "NUM_NOTACAO_CIENTIFICA",  # ponto flutuante em notaçao científica
    "NUM_PONTO_FLUTUANTE",  # ponto flutuate
    "NUM_INTEIRO",  # inteiro
    # operadores binarios
    "ADICAO",  # +
    "SUBTRACAO",  # -
    "MULTIPLICACAO",  # *
    "DIVISAO",  # /
    "E_LOGICO",  # &&
    "OU_LOGICO",  # ||
    "DIFERENCA",  # <>
    "MENOR_IGUAL",  # <=
    "MAIOR_IGUAL",  # >=
    "MENOR",  # <
    "MAIOR",  # >
    "IGUALDADE",  # =
    # operadores unarios
    "NEGACAO",  # !
    # simbolos
    "ABRE_PAR",  # (
    "FECHA_PAR",  # )
    "ABRE_COL",  # [
    "FECHA_COL",  # ]
    "VIRGULA",  # ,
    "DOIS_PONTOS",  # :
    "ATRIBUICAO",  # :=
    "COMENTARIO", # {***}
    ]

    # Palavras reservadas    
    reserved = {
    "se": "SE",
    "então": "ENTAO",
    "senão": "SENAO",
    "fim": "FIM",
    "repita": "REPITA",
    "flutuante": "FLUTUANTE",
    "retorna": "RETORNA",
    "até": "ATE",
    "leia": "LEIA",
    "escreva": "ESCREVA",
    "inteiro": "INTEIRO",
    }

    tokens = tokens + list(reserved.values())

    # Expressões Regulares para tokens simples

    # Símbolos.
    t_ADICAO    = r'\+'
    t_SUBTRACAO  = r'-'
    t_MULTIPLICACAO   = r'\*'
    t_DIVISAO = r'/'
    t_ABRE_PAR  = r'\('
    t_FECHA_PAR  = r'\)'
    t_ABRE_COL = r'\['
    t_FECHA_COL = r'\]'
    t_VIRGULA = r','
    t_ATRIBUICAO = r':='
    t_DOIS_PONTOS = r':'

    # Operadores Lógicos.
    t_E_LOGICO = r'&&'
    t_OU_LOGICO = r'\|\|'
    t_NEGACAO = r'!'

    # Operadores Relacionais.
    t_DIFERENCA = r'<>'
    t_MENOR_IGUAL = r'<='
    t_MAIOR_IGUAL = r'>='
    t_MENOR = r'<'
    t_MAIOR = r'>'
    t_IGUALDADE = r'='
    
    # Expressões Regulares para tokens complexos
    
    def t_COMENTARIO(self,t):
        r"(\{((.|\n)*?)\})"
        t.lexer.lineno += t.value.count("\n")
        pass

    def t_ID(self,t):
        r'[a-zA-Z_áÁãÃàÀéÉíÍóÓõÕ][a-zA-Z_áÁãÃàÀéÉíÍóÓõÕ0-9]*'
        t.type = self.reserved.get(t.value,'ID')
        return t

    def t_NUM_NOTACAO_CIENTIFICA(self,t):
        r'[+-]?\d*\.?\d+[eE][+-]?\d+'
        t.value = float(t.value)    
        return t

    def t_NUM_PONTO_FLUTUANTE(self,t):
        r'[+-]?(\d+\.\d+)'
        t.value = float(t.value)    
        return t

    def t_NUM_INTEIRO(self,t):
        r'[+-]?(\d+)'
        t.value = int(t.value)    
        return t

    # Regra para contar o número de linhas 
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Ignorar os espaços e tabs
    t_ignore  = ' \t'

    # Tratamento de erro
    def t_error(self,t):
        print("Caractere inválido '%s'" % t.value[0])
        t.lexer.skip(1)

    # Constrói o lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
    
    # Testar a saída
    def test(self,data,info=False):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: 
                break
            elif info:
                print(tok)
            else:    
                print(tok.type)