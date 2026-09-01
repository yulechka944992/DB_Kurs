from configparser import ConfigParser


def config(filename="database.ini", section="postgresql"):
    # create a parser
    parser = ConfigParser()
    # Пробуем разные кодировки
    encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'latin-1']

    for encoding in encodings:
        try:
            parser.read(filename, encoding=encoding)
            if parser.has_section(section):
                db = {}
                params = parser.items(section)
                for param in params:
                    db[param[0]] = param[1]
                return db
        except Exception:
            continue

    # Если ничего не сработало - ошибка
    raise Exception(
        f'Section {section} not found in {filename} or file encoding issue.'
    )