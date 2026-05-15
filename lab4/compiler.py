import re
import contextlib
import io


# Выполняет простой препроцессинг: удаляет комментарии и пустые строки.
def preprocess(text):
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

    lines = []
    for line in text.splitlines():
        line = line.rstrip()
        if line.strip() != "":
            lines.append(line)

    return "\n".join(lines)


# Подключение модулей без лишнего вывода при импорте.
with contextlib.redirect_stdout(io.StringIO()):
    import lexical_analyzer as lexer
    import syntax_analyzer as syntax
    import semantic_analyzer as semantic


filename = "test_new.cpp"


# 1. Препроцессинг
source_code = lexer.read_source_file(filename)

if source_code.strip() == "":
    print("Ошибка: входной файл пуст.")
    raise SystemExit(1)

preprocessed_code = preprocess(source_code)

print("1. Препроцессинг завершён успешно.")
print()


# 2. Лексический анализ
tokens = lexer.lexical_analyze(preprocessed_code)
lexer.validate(tokens)

print("2. Лексический анализ завершён успешно.")
print(f"Обнаружено токенов: {len(tokens)}")
print()


# 3. Синтаксический анализ
ast = syntax.syntax_analyze(tokens)

print("3. Синтаксический анализ завершён успешно.")
print("Построенное AST:")
syntax.print_ast(ast)
print()


# 4. Семантический анализ
analyzer = semantic.semantic_analyze(ast)

print("4. Семантический анализ завершён успешно.")
print("Ошибок не найдено.")
print()


# 5. Таблица символов
analyzer.print_symbols()
print()


# 6. Промежуточное представление в виде триад
analyzer.print_triads()
print()


print("Итоговый компилятор завершил полный цикл обработки программы.")