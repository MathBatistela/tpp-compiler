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
    "MAIS",  # +
    "MENOS",  # -
    "VEZES",  # *
    "DIVIDE",  # /
    "E",  # &&
    "OU",  # ||
    "DIFERENTE",  # <>
    "MENOR_IGUAL",  # <=
    "MAIOR_IGUAL",  # >=
    "MENOR",  # <
    "MAIOR",  # >
    "IGUAL",  # =
    # operadores unarios
    "NAO",  # !
    # simbolos
    "ABRE_PARENTESE",  # (
    "FECHA_PARENTESE",  # )
    "ABRE_COLCHETE",  # [
    "FECHA_COLCHETE",  # ]
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
    t_MAIS    = r'\+'
    t_MENOS  = r'-'
    t_VEZES   = r'\*'
    t_DIVIDE = r'/'
    t_ABRE_PARENTESE  = r'\('
    t_FECHA_PARENTESE  = r'\)'
    t_ABRE_COLCHETE = r'\['
    t_FECHA_COLCHETE = r'\]'
    t_VIRGULA = r','
    t_ATRIBUICAO = r':='
    t_DOIS_PONTOS = r':'

    # Operadores Lógicos.
    t_E = r'&&'
    t_OU = r'\|\|'
    t_NAO = r'!'

    # Operadores Relacionais.
    t_DIFERENTE = r'<>'
    t_MENOR_IGUAL = r'<='
    t_MAIOR_IGUAL = r'>='
    t_MENOR = r'<'
    t_MAIOR = r'>'
    t_IGUAL = r'='
    
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
        r'[+-]?(\d+\.\d*)'
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
        print("Caracter inválido '%s'" % t.value[0])
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
