def validate_field(field, to_split=False):
    if to_split and field:
        return field.split(' ')
    elif field and type(field) is str:
        return field
    elif field and type(field) is list and hasattr(field[0], 'b'):
        return field[0].b
    elif field and type(field) is list and hasattr(field[0], 'value'):
        return field[0].value
    elif field and type(field) is list:
        return field[0]
    elif field and type(field) is float:
        return field
    elif field:
        return field.value

    else:
        return None
