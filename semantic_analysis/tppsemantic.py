
import sys
sys.path.append("../syntax_analysis")

import mytree
import pandas as pd
from anytree.search import findall, find_by_attr, findall_by_attr, find
from tppparser import get_root

class Row():
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class SemanticAnalyzer:

    def __init__(self,file):
        self.root = get_root(file)
        self.set_scope()
        self.var_table = self.generate_var_table()
        print()
        self.func_table = self.generate_func_table()
        # self.error_handling()
        # self.set_atribution_asto()

    @staticmethod
    def raise_error(message,line=None):
        if line:
            message = message + f" , na linha {line}"
        print("Erro >>> " + message)
        # sys.exit()
        pass

    @staticmethod
    def raise_warning(message,line=None):
        if line:
            message = message + f" , na linha {line}"
        print("Aviso >>> " + message)
        pass

    def set_scope(self):
        functions = findall_by_attr(self.root, "cabecalho")
        for function in functions:
            scope = function.child(name="ID").child().name
            var_declarations = findall(function, filter_=lambda node: node.name in ("var", "id"))
            for var in var_declarations:
                var.scope = scope
                for child in var.children: child.scope = scope

    def generate_func_table(self):
        func_obj_rows = []

        declarations = findall_by_attr(self.root, "declaracao_funcao")

        for func in declarations:
            row = Row()
            _type = func.child(name="tipo")
            if _type:
                row.type = _type.child().name 
            else:
                row.type = "VOID"
            
            header = func.child(name="cabecalho")
            row.name = header.child(name="ID").child().name

            types_nodes = findall_by_attr(header.child(name="lista_parametros"), "tipo")
            param_list = []
            for param in types_nodes:
                param_type = param.child().name
                param_name = param.parent.child(name="id").child().name
                param_list.append((param_type,param_name))
            
            row.params = param_list
            row.n_param = len(param_list)

            row.returns = ("VOID",None)
            returns = findall_by_attr(header, "retorna")
            if returns:
                exp = returns[0].child(name="expressao")
                return_item = exp.leaves[0]
                return_type = return_item.parent.type.split("_").pop()
                row.returns = (return_type,return_item.name)
                

            row.scope = header.child(name="ID").child().scope
            row.line = header.child(name="ID").child().line
            func_obj_rows.append(row)

        func_obj_rows = [list((o.__dict__).values()) for o in func_obj_rows]
        func_table = pd.DataFrame(data=func_obj_rows, columns=["Tipo","Nome","Parametros","N-params","Retorna","Escopo","Linha"])
        print(func_table.to_markdown())
        return(func_table)

    def param_vars(self):
        var_obj_rows = []
        declarations = list(findall_by_attr(self.root, "parametro"))
        var_params = list(filter(lambda x: x.child(name="id") != None, declarations))
        for var in var_params:
            var = var.child(name="id")
            row = Row()
            row.token = "ID"
            row.lexeme = var.child().name
            row.type = var.parent.child(name="tipo").child().name
            row.dim, row.tam_dim1, row.tam_dim2 = 0, 1, 0
            row.scope, row.line = var.child().scope, var.child().line
            var_obj_rows.append(row)
        return var_obj_rows
   
        
    def generate_var_table(self):
        var_obj_rows = []

        declarations = findall_by_attr(self.root, "declaracao_variaveis")
        for list_var in declarations:
            _type = find_by_attr(list_var, "tipo").child().name

            var_list = findall_by_attr(list_var, "var")
            for var in var_list:
                if var.parent.name == "fator": break
                row = Row()
                try:
                    one_plus_d = var.child()
                    row.token = one_plus_d.name
                    row.lexeme = one_plus_d.child().name
                    row.type = _type
                    factors = findall_by_attr((var.children)[1], "fator")
                    row.dim = len(factors)
                    row.tam_dim1 = factors[0].child().child().child().name
                    row.tam_dim2 = 0
                    if row.dim == 2:
                        row.tam_dim2 = factors[1].child().child().child().name
                    row.scope = one_plus_d.scope
                    row.line = one_plus_d.child().line
                    
                except IndexError:
                    one_d = var.child()
                    row.token = one_d.name
                    row.lexeme = one_d.child().name
                    row.type = _type
                    row.dim = 0
                    row.tam_dim1 = 1
                    row.tam_dim2 = 0
                    row.scope = one_d.scope
                    row.line = one_d.child().line

                var_obj_rows.append(row)

        var_obj_rows = var_obj_rows + self.param_vars()

        var_obj_rows = [list((o.__dict__).values()) for o in var_obj_rows]
        var_table = pd.DataFrame(data=var_obj_rows, columns=["Token", "Lexema", "Tipo", "dim", "tam_dim1", "tam_dim2", "escopo", "linha"])
        print(var_table.to_markdown())
        return var_table

    @staticmethod
    def eq_atribution_asto_subtree(eq_list):
        op = eq_list[0]
        stack = eq_list[::-1]

        while len(stack)>1:
            var1 = stack.pop()
            op = stack.pop()
            var2 = stack.pop()

            var1.parent = None
            var2.parent = None
            op.children = [var1,var2]

            stack.append(op)
        return op

    def set_atribution_asto(self):

        assignment_list = findall_by_attr(self.root, "atribuicao")
        func_header_name = lambda  leaves: "".join(str(cr) for cr in [l.name for l in leaves])

        for a in assignment_list:
            indexes = findall_by_attr(a, "indice")
            if indexes:
                for index in indexes: index.parent = None

            func_calls = findall_by_attr(a, "chamada_funcao")
            if func_calls:
                for func in func_calls:
                    name = func_header_name(func.leaves)
                    func.name = name
                    for child in func.children: child.parent = None

            leaves = [x for x in a.leaves if x.name not in ['(',')']]
            eq_asto = self.eq_atribution_asto_subtree(leaves[2:])

            leaves[1].children = [leaves[0],eq_asto]

            for child in a.children: child.parent = None
            a.children = [leaves[1]]


    def error_handling(self):

        calls = findall_by_attr(self.root, "chamada_funcao")
        call_names = [call.child(name="ID").child().name for call in calls]
        not_called = [func for func in list(self.func_table.Nome) if func not in call_names]

        # Verifica erros relacionados a funcao principal
        principal = findall_by_attr(self.root, "cabecalho")
        principal = [head.child(name="ID").child() for head in principal if head.child(name="ID").child().name == "principal"]
        if principal:
            princip_calls = findall_by_attr(principal[0].parent.parent, "chamada_funcao")
            princip_call_names = [call.child(name="ID").child().name for call in princip_calls]
            if not principal[0].child(name="retorna"):
                self.raise_error("Função principal deveria retornar inteiro, mas retorna vazio")
            if "principal" in princip_call_names:
                self.raise_warning("Chamada recursiva para principal")
                not_called.append("principal")
        else:
            self.raise_error("Função principal não declarada")

        try:
            not_called.remove("principal")
        except:
            self.raise_error(f"Chamada para a função principal não permitida")
        

        # Verifica as funcoes declaradas e nao utilizadas
        not_declared = [func for func in call_names if func not in list(self.func_table.Nome)]
        for nd in not_called:
            self.raise_warning(f"Função '{nd}' declarada, mas não utilizada",
            self.func_table.loc[self.func_table.Nome == nd, 'Linha'].values[0])

        for call in calls:

            func_id = call.child(name="ID").child()
        
            # Verifica chamadas de funcao para funcoes nao declaradas 
            if func_id.name in not_declared:
                self.raise_error(f"Chamada a função '{func_id.name}' que não foi declarada",func_id.line)

            # Verifica se o numero de parametros e de acordo com o declarado
            list_arg = call.child(name="lista_argumentos")
            n_params = len(findall(list_arg, filter_=lambda node: node.name in ("var", "numero")))

            try:
                # Verifica se o retorno bate com o tipo da funcao
                table_index = self.func_table[self.func_table['Nome'] == func_id.name].index.item()
                return_type = self.func_table['Retorna'][table_index]
                func_type = self.func_table['Tipo'][table_index]

                if func_type != return_type[0]:
                    if return_type[0] == "ID":
                        if return_type[1] in self.var_table.Lexema.values:
                            var_type = self.var_table.loc[self.var_table.Lexema == return_type[1], 'Tipo'].values[0]
                            if  var_type != func_type:
                                self.raise_error(f"Função '{func_id.name}' deveria retornar {func_type.lower()}, mas retorna {var_type.lower()}")
                        else:
                            self.raise_error(f"Função '{func_id.name}' retorna um parâmetro inexistente")
        
                    elif return_type[0] != func_type:
                        self.raise_error(f"Função '{func_id.name}' deveria retornar {func_type.lower()}, mas retorna {return_type[0].lower()}")

                if self.func_table['N-params'][table_index] != n_params:
                    self.raise_error(f"Chamada à função '{func_id.name}' com número de parâmetros diferente que o declarado",func_id.line)
            except:
                pass
                
        # Verifica variaveis declaradas e não utilizadas
        var_uti = findall(self.root, filter_=lambda node: node.name in ("fator", "atribuicao"))
        
        var_uti_list = list(filter(lambda x: x.child(name="var") != None, var_uti))
        var_uti_names = [var.child(name="var").child(name="ID").child().name for var in var_uti_list]
        for declared in self.var_table.Lexema.values:
            if declared not in var_uti_names:
                self.raise_warning(f"Variável '{declared}' declarada e não utilizada")
        for uti in var_uti_names:
            if uti not in self.var_table.Lexema.values:
                self.raise_error(f"Variável '{uti}' não declarada")


        # Verifica variaveis declaradas e nao inicializadas
        var_atrib = [atrib.child().child().child().name for atrib in
            list(findall(self.root, filter_=lambda node: (node.name == "atribuicao") and (node.child(name="var") != None)))]
        for declared in self.var_table.Lexema.values:
            if declared not in var_atrib:
                self.raise_warning(f"Variável '{declared}' declarada e não inicializada")

        # Verifica variaveis duplicadas
        duplicate_layer1 = self.var_table[self.var_table.duplicated(['Lexema'], keep=False)]
        duplicate_layer2 = duplicate_layer1[duplicate_layer1.duplicated(['escopo'])]
        for duplicate in duplicate_layer2.Lexema.values: self.raise_warning(f"Variável '{duplicate}' já declarada anteriormente")

        
        assignment_list = list(findall_by_attr(self.root, "atribuicao"))
        vars_list = self.var_table[["Lexema", "Tipo"]].values
        func_list = self.func_table[["Nome", "Tipo"]].values
        for assign in assignment_list:   
            operators = list(filter(lambda n: (
             n.parent.name == "ID" or
             n.parent.name == "NUM_INTEIRO" or 
             n.parent.name == "NUM_PONTO_FLUTUANTE" 

            ) ,list(assign.leaves)))
            operators = [op.name for op in operators]
            assigned = operators.pop(0)
            assigned_type = next((var for var in vars_list if var[0] == assigned), [None,None])
      
            for value in operators:
                if type(value) is str:
                    for i in range(len(vars_list)):
                        if value in vars_list[i]:
                            if vars_list[i][1] != assigned_type[1]:
                                self.raise_warning(f"Atribuição de tipos distintos, '{assigned}' {assigned_type[1].lower()} e '{vars_list[i][0]}' {vars_list[i][1].lower()}")

                    for i in range(len(func_list)):
                        if value in func_list[i]:
                            if func_list[i][1] != assigned_type[1]:
                                self.raise_warning(f"Atribuição de tipos distintos, '{assigned}' recebe {assigned_type[1].lower()} e '{func_list[i][0]}' retorna {func_list[i][1].lower()}")
                else:
                    if type(value) is int and (assigned_type[1] == "FLUTUANTE"):
                        self.raise_warning(f"Coerção implícita do valor atribuído para '{assigned}', variável flutuante recebendo um inteiro")
                    elif type(value) is float and (assigned_type[1] == "INTEIRO"):
                        self.raise_warning(f"Coerção implícita do valor atribuído para '{assigned}', variável inteira recebendo um flutuante")

        for index, row in self.var_table.iterrows():
            if isinstance(row['tam_dim1'],str): pass
            if not float(row['tam_dim1']).is_integer() or not float(row['tam_dim2']).is_integer():
                self.raise_error(f"índice de array '{row['Lexema']}' não inteiro")

    def export_tree(self):
        from anytree.exporter import UniqueDotExporter
        UniqueDotExporter(self.root).to_picture("ex" + ".unique.ast.png")

def main():
    arg = sys.argv[1]
    if not arg.endswith('.tpp'):
        raise IOError("Not a tpp file!")
    
    data = open(arg, 'r')    
    source_file = data.read()
    data.close()

    a = SemanticAnalyzer(source_file)

    print()
    a.error_handling()
    a.set_atribution_asto()
    a.export_tree()
    print()

if __name__ == "__main__":
    main()
