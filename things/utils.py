def check_uint_param(param, default):
    if param is None:
        return default

    try:
        value = default if int(param) <= 0 else int(param)
    except ValueError:  # if param is not `int` - ignore it and set `default`
        value = default

    return value
