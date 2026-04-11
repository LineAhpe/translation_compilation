import re

# Чтение файла
def read_source_file(filename):
    with open(filename, "r", encoding="cp1251") as f:
        return f.read()

# Ключевые слова из test.cpp
KEYWORDS = {"using", "namespace", "int", "return", "if", "bool", "while", "switch", "case", "break", "default", "cout", "cin", "endl", "std"}

# Идентификаторы
IDENTIFIERS = {"summ", "a", "b", "mult", "diff", "main", "SetConsoleCP", "SetConsoleOutputCP", "fl", "choice", "iostream", "windows.h"}

# Булевы константы
BOOL_CONSTANTS = {"true", "false"}

# Операторы
OPERATORS = {"<<", ">>", "=", "+", "-", "*", ">"}

# Разделители
DELIMITERS = {"(", ")", "{", "}", ",", ";", ":"}


# Функция для вывода ошибки
def lexical_error(message, lexeme=""):
    print("Лексическая ошибка:", message)
    if lexeme:
        print("Проблемная лексема:", lexeme)
    raise SystemExit(1)


# Определение типа уже выделенной лексемы
def get_token_type(lexeme):
    if lexeme in KEYWORDS:
        return "KEYWORD"
    if lexeme in BOOL_CONSTANTS:
        return "CONSTANT_BOOL"
    if lexeme in OPERATORS:
        return "OPERATOR"
    if lexeme in DELIMITERS:
        return "DELIMITER"
    if re.fullmatch(r'\d+', lexeme):
        return "CONSTANT_INT"
    if re.fullmatch(r'\d+\.\d+', lexeme):
        return "CONSTANT_FLOAT"
    if re.fullmatch(r'"[^"\n]*"', lexeme):
        return "CONSTANT_STRING"
    if lexeme in IDENTIFIERS:
        return "IDENTIFIER"
    lexical_error("лишняя лексема", lexeme)


def validate(tokens):
    for i in range(len(tokens)):
        token_type, lexeme = tokens[i]

        if token_type not in {"IDENTIFIER", "CONSTANT_INT", "CONSTANT_FLOAT", "CONSTANT_STRING", "CONSTANT_BOOL"}:
            continue

        if i > 0:
            prev_lexeme = tokens[i - 1][1]
            prev_token = tokens[i - 1][0]
        if i + 1 < len(tokens):
            next_lexeme = tokens[i + 1][1]
            next_token = tokens[i + 1][0]

        if prev_token in {"IDENTIFIER", "CONSTANT_INT", "CONSTANT_FLOAT", "CONSTANT_STRING", "CONSTANT_BOOL"}:
            lexical_error("Две лексемы подряд без разделителя или лексеми", lexeme)
        if prev_lexeme in {":", "{", "}", ";"} and (next_lexeme in {"return", "case", "break", "default", ";", "}", "{"} or next_token in {"KEYWORD", "DELIMITER"}):
            if not (token_type == "IDENTIFIER" and next_lexeme == "("):
                lexical_error("лишняя лексема", lexeme)

# Лексический анализ
def lexical_analyze(text):
    tokens = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        # Пропускаем пробельные символы
        if ch.isspace():
            i += 1
            continue

        # Обработка #include
        if text.startswith("#include", i):
            tokens.append(("KEYWORD", "#include"))
            i += len("#include")

            # пропускаем пробелы после #include
            while i < n and text[i].isspace():
                i += 1

            # ожидаем <
            if i >= n or text[i] != '<':
                lexical_error("после #include ожидается символ <", "#include")

            tokens.append(("DELIMITER", "<"))
            i += 1

            # читаем имя заголовка до >
            start = i
            while i < n and text[i] != '>':
                i += 1

            if i >= n:
                lexical_error("после #include не найден закрывающий символ >", text[start:])

            header_name = text[start:i]
            if header_name == "":
                lexical_error("пустое имя заголовочного файла", "<>")

            tokens.append(("IDENTIFIER", header_name))
            tokens.append(("DELIMITER", ">"))
            i += 1
            continue

        # Строковые константы
        if ch == '"':
            start = i
            i += 1
            while i < n and text[i] != '"':
                if text[i] == '\n':
                    lexical_error("незакрытый строковый литерал", text[start:i])
                i += 1

            if i >= n:
                lexical_error("незакрытый строковый литерал", text[start:])

            i += 1
            lexeme = text[start:i]
            tokens.append(("CONSTANT_STRING", lexeme))
            continue

        # Двухсимвольные операторы
        if i + 1 < n:
            two = text[i:i + 2]
            if two in OPERATORS:
                tokens.append(("OPERATOR", two))
                i += 2
                continue

        # Разделители
        if ch in DELIMITERS:
            tokens.append(("DELIMITER", ch))
            i += 1
            continue

        # Односимвольные операторы
        if ch in OPERATORS:
            tokens.append(("OPERATOR", ch))
            i += 1
            continue

        # Числа
        if ch.isdigit():
            start = i
            while i < n and (text[i].isdigit() or text[i] == '.' or text[i].isalpha() or text[i] == '_'):
                i += 1

            lexeme = text[start:i]

            # Ошибка: две точки и более
            if lexeme.count('.') > 1:
                lexical_error("некорректно оформленное число: больше одной точки", lexeme)

            # Ошибка: буквы в числе или идентификатор начинается с цифры
            if re.search(r'[A-Za-z_]', lexeme):
                lexical_error("идентификатор начинается с цифры или число содержит буквы", lexeme)

            token_type = get_token_type(lexeme)
            if token_type is None:
                lexical_error("некорректно оформленное число", lexeme)

            tokens.append((token_type, lexeme))
            continue

        # Идентификаторы и ключевые слова
        if ch.isalpha() or ch == '_':
            start = i
            while i < n and (text[i].isalnum() or text[i] == '_'):
                i += 1

            lexeme = text[start:i]
            token_type = get_token_type(lexeme)

            if token_type is None:
                lexical_error("неизвестная лексема", lexeme)

            tokens.append((token_type, lexeme))
            continue

        lexical_error("недопустимый символ", ch)

    return tokens


# Запуск программы
content = read_source_file("test_new.cpp")

if content.strip() == "":
    print("Ошибка: входной файл пуст.")
    raise SystemExit(1)

tokens = lexical_analyze(content)
validate(tokens)

# Табличный вывод
print("Лексема".ljust(21) + "| Тип")
print("-" * 21 + "+" + "-" * 22)

for token_type, lexeme in tokens:
    print(lexeme.ljust(21) + "| " + token_type)

print()
print(tokens)
print()
print(f"Лексический анализ завершён успешно. Обнаружено {len(tokens)} токенов. Ошибок не найдено.")