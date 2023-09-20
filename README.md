# Hab Gui

A graphical user interface built on top of [hab](https://github.com/blurstudio/hab)
to take hab out of the shell.

![image](https://github.com/blurstudio/hab-gui/assets/2424292/c3d8247a-4026-4405-ab9b-9360ac927672)

# Features

- Gui for selecting hab URI's and launching aliases.
- Gui for setting the current uri.
- [hab gui sub-command](#hab-gui-sub-command)
- [habw](#habwexe) command allows using hab without popup consoles on windows.
- Customization of hab-gui using [entry_points](#hab-gui-entry-points) defined
in hab site json files.

# Quickstart

1. Enable the use of [`hab gui`](#hab-gui-sub-command) by adding the entry_point
in your site json file. You can use the example site files that come in the
[hab](https://github.com/blurstudio/hab/blob/main/tests/site_main.json) and
[hab-gui](https://github.com/blurstudio/hab-gui/tree/main/tests/site/hab-gui.json)
repos.

```bash
export HAB_PATHS="/path/to/hab-gui/tests/site/hab-gui.json:/path/to/hab/tests/site_main.json"
```
[hab-gui.json](tests/site/hab-gui.json) extends hab's cli by adding the
[gui comand](#hab-gui-sub-command)

2. Use hab gui to launch the alias launch window.

    ```bash
    hab gui launch
    ```
    Or update the URI saved in the [user prefs](https://github.com/blurstudio/hab#user-prefs).
    ```bash
    hab gui set-uri
    ```

## hab gui sub-command

Using [hab entry points](https://github.com/blurstudio/hab#hab-entry-points) you
can add a gui sub-command to hab. This allows you to launch hab-gui commands
from the existing hab shell commands.

```json5
{
    "prepend": {
        "entry_points": {
            "cli": {
                "gui": "hab_gui.cli:gui"
            }
        }
    }
}
```
This is a minimal [site json file](tests/site/hab-gui.json) enabling the use of `hab gui`
that can be added to your existing site files.

## habw.exe

When hab-gui is installed it adds the command `habw` as a using
[gui_scripts](https://packaging.python.org/en/latest/specifications/entry-points/#use-for-scripts).
This is useful for windows users as it prevents showing a command prompt window
while using the other hab gui features. This exe uses the same cli interface as
hab so you can convert any existing command to using habw. Just keep in mind that
you won't see any text output on windows, so you may want to only use it when
using the `hab gui` sub-command.

## Hab-gui Entry Points

By default hab-gui uses fairly simple gui interfaces like a combo box for URI picking
and simple buttons to launch aliases. Using the
[hab entry points](https://github.com/blurstudio/hab#hab-entry-points) system
you can implement your own widgets extending or completely re-implementing them.

| Feature | Description | Multiple values |
|---|---|---|
| hab_gui_init | Used to customize the init of hab gui's launched from the command line. By default this installs a `sys.excepthook` that captures any python exceptions and shows them in a QMessageBox dialog. See [hab-gui-init.json](tests/site/hab-gui-init.json). | Only the first is used, the rest are discarded. |
