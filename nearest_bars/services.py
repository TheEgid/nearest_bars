import json


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
