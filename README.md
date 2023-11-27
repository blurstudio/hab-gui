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

2. Set a HAB_PATHS environment variable.
- [Bash (Linux)](https://github.com/blurstudio/hab#bash-linux)
- [Bash (Windows, Cygwin)](https://github.com/blurstudio/hab#bash-windows-cygwin)
- [Command Prompt (Windows)](https://github.com/blurstudio/hab#command-prompt-windows-1)
- [PowerShell (Windows)](https://github.com/blurstudio/hab#powershell-windows)


[hab-gui.json](tests/site/hab-gui.json) extends hab's cli by adding the
[gui comand](#hab-gui-sub-command)

3. Use hab gui to launch the alias launch window.

    ```bash
    hab gui launch
    ```
    Or update the URI saved in the [user prefs](https://github.com/blurstudio/hab#user-prefs).
    ```bash
    hab gui set-uri
    ```

# Configuration

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

<!-- Tooltips used by the table -->
[tt-group]: ## "The hab-gui feature this entry_point is being used for."
[tt-multi]: ## "How having multiple entry_points for this group is handled."
[tt-multi-first]: ## "Only the first entry_point for this group is used, the rest are discarded."

| [Group][tt-group] | Description | Used by | [Multiple][tt-multi] |
|---|---|---|---|
| hab_gui.alias.widget | Widget used to display and launch a specific alias for the current URI. | [AliasLaunchWindow](hab_gui/windows/alias_launch_window.py) | [First][tt-multi-first] |
| hab_gui.aliases.widget | Class used to display the `hab_gui.alias.widget`'s. | [AliasLaunchWindow](hab_gui/windows/alias_launch_window.py) | [First][tt-multi-first] |
| hab_gui.init | Used to customize the init of hab gui's launched from the command line. By default this installs a `sys.excepthook` that captures any python exceptions and shows them in a QMessageBox dialog. See [hab-gui-init.json](tests/site/hab-gui-init.json). | [hab_gui.cli](hab_gui/cli.py) when starting a QApplication instance. | [First][tt-multi-first] |
| hab_gui.uri.pin.widget | Class used to allow the user to pinned commonly used URIs. Pinning can be disabled by the site file, or setting this entry_point to `null`. | [AliasLaunchWindow](hab_gui/windows/alias_launch_window.py) | [First][tt-multi-first] |
| hab_gui.uri.widget | Class used by the user to choose the current URI they want to launch aliases from. This class can be customized to provide the user with URI's generated from a DB that are not explicitly defined by configs. | [AliasLaunchWindow](hab_gui/windows/alias_launch_window.py) | [First][tt-multi-first] |

- See [hab-gui.json](tests/site/hab-gui.json) for an example of adding the `gui` sub-command to `hab`.
- See [hab-gui-alt.json](tests/site/hab-gui-alt.json) for an example of changing the default classes used by `hab gui launch`.
- See [hab-gui-init.json](tests/site/hab-gui-init.json) for an example of changing the `QApplication` before any `hab gui` commands create it. This also allows for global customization of features like error handling etc.

Note: Entry_point names should start with `hab_gui.` and use `.` between each following word following the group specification on https://packaging.python.org/en/latest/specifications/entry-points/#data-model.

## Icons and labels

For the command line using an simplified alias name that is easy to type but harder
to read is generally preferred. However for a UI like the launcher, its nice to
be able to use a nice name with spaces and extra information. For example in the
command line using the alias `maya24` is better than having to type `"Maya 2024"`
including double quotes.

Hab gui respects extra values defined on [complex aliases](https://github.com/blurstudio/hab#complex-aliases).

| Key | Description | Default |
|---|---|---|
| icon | Path to a icon file readable by QIcon. | No icon is shown. |
| label | The text to show instead of the alias name. | Same alias name shown in command line. |
| [min_verbosity](https://github.com/blurstudio/hab#min_verbosity) | Hab-gui uses the `hab-gui` key. For example `"min_verbosity": {"global": 1, "hab-gui": 3}` would make this alias visible on the command line using `-v` or above, but when using hab-gui you would need to use `-vvv` or higher to see it. This allows you to hide aliases that only make sense on the command line but not in hab-gui. | 0, so always visible. |

Example:
```json5
{
    "name": "maya2024",
    "aliases": {
        "windows": [
            [
                // Alias users are expected to launch the correct version of maya with
                "maya", {
                    "cmd": "C:\\Program Files\\Autodesk\\Maya2024\\bin\\maya.exe",
                    // Show the icon and give it the nice name "Maya"
                    "icon": "{relative_root}/.img/maya.ico",
                    "label": "Maya",
                }
            ],
            [
                // Alias used to launch Maya 2024. This allows you to also have
                // access to Maya 2023 etc in the same config and launch the
                // correct version.
                "maya24", {
                    "cmd": "C:\\Program Files\\Autodesk\\Maya2024\\bin\\maya.exe",
                    "icon": "{relative_root}/.img/maya.ico",
                    "label": "Maya 2024",
                    // In general we don't want users to have to know which version
                    // of Maya to launch so hide this alias unless the user passes `-v`
                    // when using the command line or hab-gui.
                    "min_verbosity": {"global": 1},
                }
            ],
            // The mayapy alias are being added for script access and are not really
            // meant for users, so hide them from the command line.
            // Hab-gui can't pass arguments to aliases when launching, so there
            // really is no need to show this alias in hab-gui, so require `-vvv`.
            [
                "mayapy", {
                    "cmd": "C:\\Program Files\\Autodesk\\Maya2024\\bin\\mayapy.exe",
                    "min_verbosity": {"global": 1, "hab-gui": 3},
                }
            ],
            [
                "mayapy24", {
                    "cmd": "C:\\Program Files\\Autodesk\\Maya2024\\bin\\mayapy.exe",
                    "min_verbosity": {"global": 1, "hab-gui": 3},
                }
            ]
        ]
    }
}
```
## Startup Splash Screen
A splash screen be enabled by adding image/directory paths to the site.json config.
The config takes a list entry and can contain full file paths or directory paths
that contain valid images.

Valid image types: JPG, PNG, GIF

```json5
{
    "prepend": {
        "splash_screen": [
            "Path(s)/To/Images"
        ]
    }
}
```

## Auto Refresh

Users are likely to keep the hab launcher open for long periods of time and this
may lead to them using out of date configuration settings. Hab Launcher has a
refresh button to let users manually force a refresh. Note that this does not
refresh the site configuration, configs and distros.

By default it will automatically refresh every 30 minutes(`00:30:00`). You can
configure this interval by setting `hab_gui_refresh_inverval` in your site
configuration. This accepts a string in `%H:%M:%S` format using
[time.strptime](https://docs.python.org/3/library/time.html#time.strptime). An
empty string will disable this auto-refresh feature.
