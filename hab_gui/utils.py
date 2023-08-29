def make_button_coords(button_list, wrap_length, arrangement):
    """Generates a dict that contains an alias_name key and a value that holds
    a 2D coordinate list.
    """
    array = dict()
    col = 0
    row = 0
    for i in range(0, len(button_list)):
        array[button_list[i]] = [row, col]
        if arrangement == 0:
            col += 1
            if col >= wrap_length:
                row += 1
                col = 0
        else:
            row += 1
            if row >= wrap_length:
                col += 1
                row = 0
    return array
