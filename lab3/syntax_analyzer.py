# Класс узла абстрактного синтаксического дерева.
class ASTNode:
    # Инициализирует узел AST с именем, значением и списком дочерних элементов.
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []

    # Добавляет дочерний узел к текущему узлу AST.
    def add(self, child):
        if child is not None:
            self.children.append(child)
        return child

    # Возвращает текстовое название узла для вывода дерева.
    def title(self):
        return f"{self.name} {self.value}" if self.value is not None else self.name

    # Формирует строки для древовидного отображения узла и его потомков.
    def to_tree(self, prefix="", is_last=True):
        lines = []
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + self.title())
        next_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            lines.extend(child.to_tree(next_prefix, i == len(self.children) - 1))
        return lines


# Выводит AST в виде дерева на экран.
def print_ast(root):
    print(root.title())
    for i, child in enumerate(root.children):
        for line in child.to_tree("", i == len(root.children) - 1):
            print(line)


# Класс синтаксического анализатора, выполняющего разбор токенов методом рекурсивного спуска.
class Parser:
    TYPE_WORDS = {"int", "bool"}
    BINARY_OPERATORS = {"+", "-", "*", ">"}

    # Инициализирует анализатор списком токенов и начальной позицией.
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # Возвращает текущий токен или EOF, если токены закончились.
    def current(self):
        if self.pos >= len(self.tokens):
            return ("EOF", "EOF")
        return self.tokens[self.pos]

    # Возвращает следующий токен без изменения текущей позиции.
    def next_token(self):
        if self.pos + 1 >= len(self.tokens):
            return ("EOF", "EOF")
        return self.tokens[self.pos + 1]

    # Проверяет, соответствует ли текущий токен ожидаемому типу и лексеме.
    def check(self, token_type=None, lexeme=None):
        t_type, t_lexeme = self.current()
        if token_type is not None and t_type != token_type:
            return False
        if lexeme is not None and t_lexeme != lexeme:
            return False
        return True

    # Проверяет текущий токен и при совпадении переходит к следующему.
    def match(self, token_type=None, lexeme=None):
        if self.check(token_type, lexeme):
            token = self.current()
            self.pos += 1
            return token
        return None

    # Проверяет наличие ожидаемого токена и выдаёт ошибку при несовпадении.
    def expect(self, token_type=None, lexeme=None, expected=""):
        token = self.match(token_type, lexeme)
        if token is not None:
            return token

        if not expected:
            if token_type and lexeme:
                expected = f"{token_type} '{lexeme}'"
            elif token_type:
                expected = token_type
            elif lexeme:
                expected = f"'{lexeme}'"
            else:
                expected = "другая лексема"

        self.error(expected)

    # Выводит сообщение о синтаксической ошибке и завершает программу.
    def error(self, expected):
        token_type, lexeme = self.current()
        message = (
            "Синтаксическая ошибка\n"
            f"Позиция токена: {self.pos + 1}\n"
            f"Найдено: ({token_type}, {lexeme})\n"
            f"Ожидалось: {expected}"
        )
        print(message)
        raise SystemExit(1)

    # Разбирает всю программу и формирует корневой узел Program.
    def parse_program(self):
        program = ASTNode("Program")

        while self.check("KEYWORD", "#include"):
            program.add(self.parse_include())

        if self.check("KEYWORD", "using"):
            program.add(self.parse_using_namespace())

        while not self.check("EOF", "EOF"):
            program.add(self.parse_function())

        return program

    # Разбирает директиву подключения библиотеки include.
    def parse_include(self):
        self.expect("KEYWORD", "#include", "директива #include")
        self.expect("DELIMITER", "<", "разделитель <")
        header = self.expect("IDENTIFIER", expected="имя подключаемой библиотеки")
        self.expect("DELIMITER", ">", "разделитель >")

        node = ASTNode("Include")
        node.add(ASTNode("Library", header[1]))
        return node

    # Разбирает конструкцию using namespace.
    def parse_using_namespace(self):
        self.expect("KEYWORD", "using", "ключевое слово using")
        self.expect("KEYWORD", "namespace", "ключевое слово namespace")
        namespace_name = self.current()
        if namespace_name[1] != "std":
            self.error("имя пространства имён std")
        self.pos += 1
        self.expect("DELIMITER", ";", "разделитель ;")

        node = ASTNode("UsingNamespace")
        node.add(ASTNode("Identifier", namespace_name[1]))
        return node

    # Разбирает тип данных int или bool.
    def parse_type(self):
        token_type, lexeme = self.current()
        if token_type == "KEYWORD" and lexeme in self.TYPE_WORDS:
            self.pos += 1
            return ASTNode("Type", lexeme)
        self.error("тип данных int или bool")

    # Разбирает определение функции.
    def parse_function(self):
        type_node = self.parse_type()
        name = self.expect("IDENTIFIER", expected="имя функции")
        self.expect("DELIMITER", "(", "разделитель (")

        params = None
        if not self.check("DELIMITER", ")"):
            params = self.parse_parameters()

        self.expect("DELIMITER", ")", "разделитель )")
        body = self.parse_body()

        node = ASTNode("Function", name[1])
        node.add(type_node)
        node.add(params)
        node.add(body)
        return node

    # Разбирает список параметров функции.
    def parse_parameters(self):
        node = ASTNode("Parameters")
        node.add(self.parse_parameter())
        while self.match("DELIMITER", ","):
            node.add(self.parse_parameter())
        return node

    # Разбирает один параметр функции.
    def parse_parameter(self):
        node = ASTNode("Parameter")
        node.add(self.parse_type())
        name = self.expect("IDENTIFIER", expected="имя параметра")
        node.add(ASTNode("Identifier", name[1]))
        return node

    # Разбирает тело функции, цикла, условия или другой блочной конструкции.
    def parse_body(self):
        self.expect("DELIMITER", "{", "открывающая фигурная скобка {")
        node = ASTNode("Body")

        while not self.check("DELIMITER", "}"):
            if self.check("EOF", "EOF"):
                self.error("закрывающая фигурная скобка }")
            node.add(self.parse_statement())

        self.expect("DELIMITER", "}", "закрывающая фигурная скобка }")
        return node

    # Определяет тип текущего оператора и вызывает соответствующую функцию разбора.
    def parse_statement(self):
        token_type, lexeme = self.current()

        if token_type == "KEYWORD" and lexeme in self.TYPE_WORDS:
            return self.parse_var_decl()
        if self.check("KEYWORD", "return"):
            return self.parse_return()
        if self.check("KEYWORD", "if"):
            return self.parse_if()
        if self.check("KEYWORD", "while"):
            return self.parse_while()
        if self.check("KEYWORD", "switch"):
            return self.parse_switch()
        if self.check("KEYWORD", "cout"):
            return self.parse_output()
        if self.check("KEYWORD", "cin"):
            return self.parse_input()
        if self.check("KEYWORD", "break"):
            return self.parse_break()

        if token_type == "IDENTIFIER":
            if self.next_token()[1] == "(":
                return self.parse_call_stmt()
            if self.next_token()[1] == "=":
                return self.parse_assign()

        self.error("оператор, объявление переменной или вызов функции")

    # Разбирает объявление одной или нескольких переменных.
    def parse_var_decl(self):
        node = ASTNode("VarDecl")
        node.add(self.parse_type())
        node.add(self.parse_decl_item())

        while self.match("DELIMITER", ","):
            node.add(self.parse_decl_item())

        self.expect("DELIMITER", ";", "разделитель ; после объявления переменной")
        return node

    # Разбирает одну переменную в объявлении и её возможную инициализацию.
    def parse_decl_item(self):
        name = self.expect("IDENTIFIER", expected="имя переменной")
        item = ASTNode("Identifier", name[1])

        if self.match("OPERATOR", "="):
            init = ASTNode("InitValue")
            init.add(self.parse_expression())
            item.add(init)

        return item

    # Разбирает оператор return.
    def parse_return(self):
        self.expect("KEYWORD", "return", "ключевое слово return")
        node = ASTNode("Return")
        node.add(self.parse_expression())
        self.expect("DELIMITER", ";", "разделитель ; после return")
        return node

    # Разбирает условный оператор if.
    def parse_if(self):
        self.expect("KEYWORD", "if", "ключевое слово if")
        self.expect("DELIMITER", "(", "разделитель ( после if")
        condition = ASTNode("Condition")
        condition.add(self.parse_expression())
        self.expect("DELIMITER", ")", "разделитель ) после условия if")

        node = ASTNode("If")
        node.add(condition)
        node.add(self.parse_body())
        return node

    # Разбирает цикл while.
    def parse_while(self):
        self.expect("KEYWORD", "while", "ключевое слово while")
        self.expect("DELIMITER", "(", "разделитель ( после while")
        condition = ASTNode("Condition")
        condition.add(self.parse_expression())
        self.expect("DELIMITER", ")", "разделитель ) после условия while")

        node = ASTNode("While")
        node.add(condition)
        node.add(self.parse_body())
        return node

    # Разбирает оператор выбора switch.
    def parse_switch(self):
        self.expect("KEYWORD", "switch", "ключевое слово switch")
        self.expect("DELIMITER", "(", "разделитель ( после switch")
        node = ASTNode("Switch")
        node.add(self.parse_expression())
        self.expect("DELIMITER", ")", "разделитель ) после switch")
        self.expect("DELIMITER", "{", "открывающая фигурная скобка switch")

        while not self.check("DELIMITER", "}"):
            if self.check("EOF", "EOF"):
                self.error("закрывающая фигурная скобка switch")
            if self.check("KEYWORD", "case"):
                node.add(self.parse_case())
            elif self.check("KEYWORD", "default"):
                node.add(self.parse_default())
            else:
                self.error("case, default или закрывающая скобка }")

        self.expect("DELIMITER", "}", "закрывающая фигурная скобка switch")
        return node

    # Разбирает ветвь case внутри switch.
    def parse_case(self):
        self.expect("KEYWORD", "case", "ключевое слово case")
        node = ASTNode("Case")
        node.add(self.parse_expression())
        self.expect("DELIMITER", ":", "разделитель : после case")
        node.add(self.parse_case_body())
        return node

    # Разбирает ветвь default внутри switch.
    def parse_default(self):
        self.expect("KEYWORD", "default", "ключевое слово default")
        self.expect("DELIMITER", ":", "разделитель : после default")
        node = ASTNode("Default")
        node.add(self.parse_case_body())
        return node

    # Разбирает тело ветви case или default.
    def parse_case_body(self):
        body = ASTNode("Body")
        while not self.check("KEYWORD", "case") and not self.check("KEYWORD", "default") and not self.check("DELIMITER", "}"):
            if self.check("EOF", "EOF"):
                self.error("case, default или закрывающая скобка }")
            body.add(self.parse_statement())
        return body

    # Разбирает оператор break.
    def parse_break(self):
        self.expect("KEYWORD", "break", "ключевое слово break")
        self.expect("DELIMITER", ";", "разделитель ; после break")
        return None

    # Разбирает оператор ввода cin.
    def parse_input(self):
        self.expect("KEYWORD", "cin", "оператор ввода cin")
        node = ASTNode("Input")

        self.expect("OPERATOR", ">>", "оператор ввода >>")
        name = self.expect("IDENTIFIER", expected="переменная для ввода")
        node.add(ASTNode("Identifier", name[1]))

        while self.match("OPERATOR", ">>"):
            name = self.expect("IDENTIFIER", expected="переменная для ввода")
            node.add(ASTNode("Identifier", name[1]))

        self.expect("DELIMITER", ";", "разделитель ; после cin")
        return node

    # Разбирает оператор вывода cout.
    def parse_output(self):
        self.expect("KEYWORD", "cout", "оператор вывода cout")
        node = ASTNode("Output")

        self.expect("OPERATOR", "<<", "оператор вывода <<")
        node.add(self.parse_output_part())

        while self.match("OPERATOR", "<<"):
            node.add(self.parse_output_part())

        self.expect("DELIMITER", ";", "разделитель ; после cout")
        return node

    # Разбирает одну часть выражения вывода cout.
    def parse_output_part(self):
        if self.check("KEYWORD", "endl"):
            self.pos += 1
            return ASTNode("Identifier", "endl")
        return self.parse_expression()

    # Разбирает вызов функции как отдельный оператор.
    def parse_call_stmt(self):
        node = self.parse_call_expr()
        node.name = "Call"
        self.expect("DELIMITER", ";", "разделитель ; после вызова функции")
        return node

    # Разбирает вызов функции внутри выражения или оператора.
    def parse_call_expr(self):
        name = self.expect("IDENTIFIER", expected="имя вызываемой функции")
        self.expect("DELIMITER", "(", "разделитель ( в вызове функции")

        node = ASTNode("CallExpr")
        node.add(ASTNode("Identifier", name[1]))
        args = ASTNode("Arguments")

        if not self.check("DELIMITER", ")"):
            args.add(self.parse_expression())
            while self.match("DELIMITER", ","):
                args.add(self.parse_expression())

        node.add(args)
        self.expect("DELIMITER", ")", "разделитель ) в вызове функции")
        return node

    # Разбирает оператор присваивания.
    def parse_assign(self):
        name = self.expect("IDENTIFIER", expected="переменная слева от присваивания")
        self.expect("OPERATOR", "=", "оператор присваивания =")

        node = ASTNode("Assign")
        node.add(ASTNode("Identifier", name[1]))
        node.add(self.parse_expression())
        self.expect("DELIMITER", ";", "разделитель ; после присваивания")
        return node

    # Разбирает выражение с бинарными операторами.
    def parse_expression(self):
        left = self.parse_primary()

        while self.current()[1] in self.BINARY_OPERATORS:
            operator = self.current()[1]
            self.pos += 1
            right = self.parse_primary()

            expr = ASTNode("BinaryExpr")
            expr.add(left)
            expr.add(ASTNode("Operator", operator))
            expr.add(right)
            left = expr

        return left

    # Разбирает простое выражение: константу, идентификатор, вызов функции или выражение в скобках.
    def parse_primary(self):
        token_type, lexeme = self.current()

        if token_type == "CONSTANT_INT":
            self.pos += 1
            return ASTNode("ConstInt", lexeme)
        if token_type == "CONSTANT_FLOAT":
            self.pos += 1
            return ASTNode("ConstFloat", lexeme)
        if token_type == "CONSTANT_STRING":
            self.pos += 1
            return ASTNode("StringConst", lexeme)
        if token_type == "CONSTANT_BOOL":
            self.pos += 1
            return ASTNode("BoolConst", lexeme)

        if token_type == "IDENTIFIER":
            if self.next_token()[1] == "(":
                return self.parse_call_expr()
            self.pos += 1
            return ASTNode("Identifier", lexeme)

        if token_type == "KEYWORD" and lexeme == "endl":
            self.pos += 1
            return ASTNode("Identifier", lexeme)

        if self.match("DELIMITER", "("):
            expr = self.parse_expression()
            self.expect("DELIMITER", ")", "закрывающая скобка выражения")
            return expr

        self.error("идентификатор, константа или вызов функции")


# Запускает синтаксический анализ и возвращает построенное AST.
def syntax_analyze(tokens):
    parser = Parser(tokens)
    ast = parser.parse_program()
    return ast


import contextlib
import io

with contextlib.redirect_stdout(io.StringIO()):
    import lexical_analyzer as lexer

filename = "test_new.cpp"
content = lexer.read_source_file(filename)

if content.strip() == "":
    print("Ошибка: входной файл пуст.")
    raise SystemExit(1)

tokens = lexer.lexical_analyze(content)
lexer.validate(tokens)

ast = syntax_analyze(tokens)

print("Результат")
print_ast(ast)
print()
print("Синтаксический анализ завершён успешно. Ошибок не найдено.")