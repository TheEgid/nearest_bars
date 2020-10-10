import json
import codecs


def storage_json_io_decorator(storage_file_pathname):
    def memoize(func):
        def decorate(*args, **kwargs):
            try:
                with open(storage_file_pathname, 'r', encoding='utf-8') as fl:
                    var_data = json.load(fl)
                return var_data
            except (FileNotFoundError, IOError):
                var_data = func(*args, **kwargs)
                with open(storage_file_pathname, 'w', encoding='utf-8') as fl:
                    json.dump(var_data, fl, ensure_ascii=False)
                return var_data
        return decorate
    return memoize


def convert_utf8(json_file):
    try:
        with codecs.open(json_file, 'r', 'utf-8') as f1:
            contents = f1.read()
    except UnicodeDecodeError:
        with open(json_file, 'r') as f1:
            contents = f1.read()
    with open(json_file, 'w', encoding='utf-8') as f2:
        f2.write(contents)
