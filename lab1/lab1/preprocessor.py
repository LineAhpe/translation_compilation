import re

tabs_spaces_pattern = r"^[ \t]+|[ \t]+$"
empty_lines_pattern = r"^\n+|\n+\Z"
one_line_comments_pattern = r"//[^\n]*"
many_lines_comments_pattern = r"/\*.*?\*/"
extra_spaces_pattern = r"[ \t]{2,}"

with open("test.cpp", "r") as f:
    content = f.read()

# Поиск незакрытых/неоткрытым многострочных комментариев
balance = 0
last_open = None

for match in re.finditer(r"/\*|\*/", content):
    if match[0] == "/*":
        balance += 1
        if balance == 1:
            last_open = match.start()
    else:
        balance -= 1
        if balance < 0:
            print(f"Лишнее закрытие */ в индексе {match.start()}")
            raise SystemExit(1)
else:
    if balance > 0:
        print(f"Незакрытый /* начиная с индекса {last_open}")
        raise SystemExit(1)

# Проверка кода на недопустимые символы
invalid_chars = re.search(r"[^\t\n\r -~А-Яа-яЁё]", content)
if invalid_chars:
    print(f"В коде есть недопустимы символ в индексе {invalid_chars.start()} {invalid_chars[0]}")
    raise SystemExit(1)

# Очистка кода с помощью регулярных выражений
content = re.sub(many_lines_comments_pattern, "", content, flags=re.DOTALL)
content = re.sub(one_line_comments_pattern, "", content)

content = re.sub(tabs_spaces_pattern, "", content, flags=re.MULTILINE)
content = re.sub(empty_lines_pattern, "", content, flags=re.MULTILINE)
content = re.sub(extra_spaces_pattern, " ", content)

# Проверка, что файл не пустой
if content.strip() == "":
    print("После очистки файл пуст.")
    raise SystemExit(1)

print(content)
print("КоД успешно очищен, ошибок не найдено")

with open("test_new.cpp", "w") as file:
    file.write(content)
    print("Очищенный код успешно сохранён в новый test_new.cpp файл.")
