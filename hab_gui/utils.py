import os


def entry_point_init(resolver, cmd, cli_args=None, **kwargs):
    """Used to apply startup configuration via site config.

    Example of site config replicating the default:
        {
            "append": {
                "entry_points": {
                    "hab_gui_init": {
                        "init": "hab_gui.entry_points.message_box:MessageBoxInit"
                    }
                }
            }
        }

    This uses the site entry_point `hab_gui_init` to initialize a class using
    the interface defined by `hab_gui.entry_points.BaseInit`. Defaults to
    `hab_gui.entry_points.message_box:MessageBoxInit` which shows a QMessageBox if
    any exceptions are raised. This prevents Qt from closing the application due
    to unhanded exceptions. If you want to disable this entry point default set
    the object reference to a empty string.

    Example of disabling entry point:
        {"append": {"entry_points": {"hab_gui_init": {"init": ""}}}}`
    """
    if cli_args is None:
        cli_args = {}

    default = {"init": "hab_gui.entry_points.message_box:MessageBoxInit"}

    # NOTE: kwargs should be added to allow for future changes to this call
    eps = resolver.site.entry_points_for_group("hab_gui_init", default=default)
    for ep in eps:
        if not ep.value:
            # Passing an empty value disables processing this entry point
            continue

        # Evaluate the entry point and initialize it
        func = ep.load()
        func(resolver, cmd, cli_args=cli_args, **kwargs)


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


def get_splash_image(resolver):
    """
    Randomly grabs an image to use as a splash screen while starting Hab-Gui.

    Valid image formats: JPG, PNG, GIF

    A resolver object will be used to grab a site.json config that defines paths
    to any image or image directory.  Those will be distilled down to a list of
    valid images that can be used by the Hab-Gui SplashScreen class.  This method
    will then randomly choose an image from that list.
    """
    resolved_list = []
    valid_extentions = [".jpg", ".png", ".gif"]
    for item in resolver.site.get("splash_screen", {}):
        if os.path.isdir(item):
            for scan_obj in os.scandir(item):
                if scan_obj.is_file:
                    if any(x in scan_obj.name for x in valid_extentions):
                        print(scan_obj.name)
                        resolved_list.append(scan_obj.path)
    import random

    return random.choice(resolved_list)
