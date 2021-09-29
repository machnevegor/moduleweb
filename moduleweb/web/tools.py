def validate_type(value: object, types: list):
    if not isinstance(types, list):
        types = [types]

    for type in types:
        if isinstance(value, object) and type in str(value):
            return True
    return False


def find_type(values: list, type: str):
    suitable_values = []
    for value in values:
        if validate_type(value, type):
            suitable_values.append(value)
    return suitable_values
