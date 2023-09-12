def make_button_coords(button_list, wrap_length, arrangement):
    array = dict()
    col = 0
    row = 0
    for i in range(0, len(button_list)):
        array[button_list[i]] = [row, col]
        if arrangement == "col":
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
