def fill_optional_fields(input_dict, optional_fields):
    res = dict(input_dict)
    for field in optional_fields:
        try:
            res[field]
        except KeyError:
            res[field] = None
    return res