from hab.solvers import Solver
from hab.utils import NotSet
from Qt.QtCore import QTimer

from .. import utils
from .name_picker import NamePicker


class DistroPicker(NamePicker):
    """A widget for picking from a list of optional distros.

    This displays the `optional_distros` config setting. Any distros checked use
    `hab.Resolver.forced_requirements` to load those distros. See the cli argument
    `--requirement` for more info.
    """

    pref_name = "distro_picker"

    def __init__(self, settings, title="Options", label="Distro", parent=None):
        super().__init__(settings, title=title, label=label, parent=parent)
        # This widget needs to update the hab resolver before other widgets
        # are updated. This signal is used to update forced_requirements.
        self.settings.uri_changing.connect(self.refresh)

    def item_changed(self, item, column):
        """Called when a item is modified, saves the user prefs when a checked
        state is updated and updates the displayed aliases."""
        super().item_changed(item, column)
        # Ensure the UI is updated with the new forced_requirements
        self.update_requirements()
        QTimer.singleShot(0, self.uri_changed)

    def reset_to_default(self):
        """Reset the checked state of names to the default values, clearing
        saved user_prefs for the current URI.
        """
        super().reset_to_default()
        # Refresh the alias button widget
        self.update_requirements()
        self.uri_changed()

    def update_requirements(self):
        # Ensure the UI is updated with the new forced_requirements
        selected = self.selected()
        forced_requirements = Solver.simplify_requirements(list(selected))

        # Preserve any requirements passed via the cli.
        cli_reqs = self.settings.resolver.__forced_requirements__
        if cli_reqs:
            # If the same distro is specified, the GUI's requirement should win.
            forced_requirements = dict(cli_reqs, **forced_requirements)

        self.settings.resolver.forced_requirements = forced_requirements

    def uri_changed(self):
        """Work function that forces the gui to update its aliases."""

        # The refresh method is called when this signal is emitted, don't
        # double process it by blocking signals.
        with utils.block_signals([self.name_tree]):
            self.settings.uri_changed.emit(self.settings.uri)

    def refresh(self, uri):
        resolver = self.settings.resolver
        cfg = resolver.resolve(uri)
        optional = cfg.optional_distros
        if optional is NotSet:
            optional = {}
        self.set_names(optional, uri=uri)

        # Ensure the alias_buttons widget has the updated requirements before
        # it refreshes from the `uri_changed` signal emited later.
        self.update_requirements()
