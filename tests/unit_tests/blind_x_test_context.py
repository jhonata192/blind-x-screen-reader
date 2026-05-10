# Blind-X Test Context - Test Isolation Framework
#
# Copyright 2025 Igalia, S.L.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Test isolation framework for Blind-X screen reader tests."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Atspi", "2.0")
gi.require_version("Gio", "2.0")
from gi.repository import Atspi, Gio, GLib  # pylint: disable=wrong-import-position

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock import MockerFixture


class BlindXTestContext:
    """Test isolation framework for Blind-X tests."""

    def __init__(self, mocker: MockerFixture, monkeypatch: MonkeyPatch):
        """Initialize the test context."""

        self.mocker: MockerFixture = mocker
        self.monkeypatch: MonkeyPatch = monkeypatch
        self.patches: dict[str, Any] = {}
        self.mocks: dict[str, MagicMock] = {}

    def patch(self, target: str, **kwargs) -> MagicMock:
        """Convenience method for creating patches."""

        return self.mocker.patch(target, **kwargs)

    def patch_object(self, target: object, attribute: str, **kwargs) -> MagicMock:
        """Convenience method for patching object attributes."""

        return self.mocker.patch.object(target, attribute, **kwargs)

    def Mock(self, **kwargs) -> MagicMock:  # pylint: disable=invalid-name
        """Convenience method for creating Mock objects."""

        return self.mocker.Mock(**kwargs)

    def patch_env(
        self,
        env_vars: dict[str, str],
        remove_vars: list[str] | None = None,
    ) -> MagicMock | None:
        """Convenience method for patching environment variables."""

        if remove_vars:
            for var in remove_vars:
                if var in os.environ:
                    del os.environ[var]

        if env_vars:
            return self.mocker.patch.dict(os.environ, env_vars)
        return None

    def patch_module(self, module_name: str, mock_module: Any) -> MagicMock:
        """Convenience method for patching sys.modules entries."""

        return self.mocker.patch.dict(sys.modules, {module_name: mock_module})

    def patch_modules(self, modules: dict[str, Any]) -> MagicMock:
        """Convenience method for patching multiple sys.modules entries."""

        return self.mocker.patch.dict(sys.modules, modules)

    def _setup_required_imports(self) -> None:
        """Sets up commonly required module imports that real modules need."""

        required_modules = [
            "blind_x.blind_x_i18n",
            "blind_x.cmdnames",
            "blind_x.input_event",
            "blind_x.keybindings",
            "blind_x.messages",
            "blind_x.text_attribute_names",
        ]

        for module_name in required_modules:
            if module_name not in self.mocks:
                mock_module = self.mocker.patch(module_name, create=True)
                if module_name == "blind_x.blind_x_i18n":
                    mock_module._ = lambda x: x
                self.mocks[module_name] = mock_module

    def _setup_essential_modules(self, module_names: list[str]) -> dict[str, MagicMock]:
        """Returns dictionary mapping module names to mock objects."""

        essential_modules = {}
        for module_name in module_names:
            mock_module = self.mocker.Mock()
            self.patch_module(module_name, mock_module)
            essential_modules[module_name] = mock_module
        return essential_modules

    def setup_shared_dependencies(
        self,
        additional_modules: list[str] | None = None,
    ) -> dict[str, MagicMock]:
        """Returns common/shared dependencies used across most Blind-X test modules."""

        core_modules = [
            "blind_x.debug",
            "blind_x.messages",
            "blind_x.input_event",
            "blind_x.keybindings",
            "blind_x.cmdnames",
            "blind_x.ax_object",
            "blind_x.dbus_service",
            "blind_x.script_manager",
            "blind_x.blind_x_i18n",
            "blind_x.guilabels",
            "blind_x.text_attribute_names",
            "blind_x.focus_manager",
            "blind_x.braille",
            "blind_x.orca_platform",
        ]

        if additional_modules:
            core_modules.extend(additional_modules)

        essential_modules = self._setup_essential_modules(core_modules)
        self.configure_shared_module_behaviors(essential_modules)
        return essential_modules

    # pylint: disable-next=too-many-locals, too-many-statements, too-many-branches
    def configure_shared_module_behaviors(self, essential_modules: dict[str, MagicMock]) -> None:
        """Configure standard behaviors for shared modules to reduce duplication."""

        if "blind_x.blind_x_i18n" in essential_modules:
            i18n_mock = essential_modules["blind_x.blind_x_i18n"]
            i18n_mock._ = lambda x: x
            i18n_mock.C_ = lambda c, x: x
            i18n_mock.ngettext = lambda s, p, n: s if n == 1 else p

        if "blind_x.debug" in essential_modules:
            debug_mock = essential_modules["blind_x.debug"]
            debug_mock.LEVEL_INFO = 800
            debug_mock.LEVEL_SEVERE = 1000
            debug_mock.print_message = self.mocker.Mock()
            debug_mock.print_tokens = self.mocker.Mock()
            debug_mock.println = self.mocker.Mock()

        if "blind_x.keybindings" in essential_modules:
            keybindings_mock = essential_modules["blind_x.keybindings"]
            bindings_instance = self.mocker.Mock()
            bindings_instance.is_empty = self.mocker.Mock(return_value=True)
            bindings_instance.add = self.mocker.Mock()
            keybindings_mock.KeyBindings = self.mocker.Mock(return_value=bindings_instance)
            keybindings_mock.KeyBinding = self.mocker.Mock(return_value=self.mocker.Mock())
            keybindings_mock.DEFAULT_MODIFIER_MASK = 1
            keybindings_mock.ORCA_SHIFT_MODIFIER_MASK = 2

        if "blind_x.focus_manager" in essential_modules:
            focus_manager_mock = essential_modules["blind_x.focus_manager"]
            manager_instance = self.mocker.Mock()
            manager_instance.get_locus_of_focus = self.mocker.Mock(return_value=None)
            manager_instance.set_locus_of_focus = self.mocker.Mock()
            manager_instance.in_say_all = self.mocker.Mock(return_value=False)
            manager_instance.is_in_preferences_window = self.mocker.Mock(return_value=False)
            manager_instance.get_active_mode_and_object_of_interest = self.mocker.Mock(
                return_value=(None, None),
            )
            focus_manager_mock.get_manager = self.mocker.Mock(return_value=manager_instance)
            focus_manager_mock.OBJECT_NAVIGATOR = "object-navigator"
            essential_modules["focus_manager_instance"] = manager_instance

        if "blind_x.dbus_service" in essential_modules:
            dbus_service_mock = essential_modules["blind_x.dbus_service"]
            controller_mock = self.mocker.Mock()
            controller_mock.register_decorated_module = self.mocker.Mock()
            dbus_service_mock.get_remote_controller = self.mocker.Mock(return_value=controller_mock)
            dbus_service_mock.command = lambda func: func
            dbus_service_mock.getter = lambda func: func
            dbus_service_mock.setter = lambda func: func
            dbus_service_mock.parameterized_command = lambda func: func

        if "blind_x.script_manager" in essential_modules:
            script_manager_mock = essential_modules["blind_x.script_manager"]
            manager_instance = self.mocker.Mock()
            script_instance = self.mocker.Mock()
            script_instance.present_message = self.mocker.Mock()
            script_instance.present_object = self.mocker.Mock()
            script_instance.speak_message = self.mocker.Mock()
            script_instance.update_braille = self.mocker.Mock()
            speech_gen = self.mocker.Mock()
            braille_gen = self.mocker.Mock()
            script_instance.get_speech_generator = self.mocker.Mock(return_value=speech_gen)
            script_instance.get_braille_generator = self.mocker.Mock(return_value=braille_gen)
            manager_instance.get_active_script = self.mocker.Mock(return_value=script_instance)
            manager_instance.get_script = self.mocker.Mock(return_value=script_instance)
            manager_instance.get_manager = self.mocker.Mock(return_value=manager_instance)
            script_manager_mock.get_manager = self.mocker.Mock(return_value=manager_instance)

        if "blind_x.ax_object" in essential_modules:
            ax_object_mock = essential_modules["blind_x.ax_object"]
            ax_object_class_mock = self.mocker.Mock()
            ax_object_class_mock.is_valid = self.mocker.Mock(return_value=True)
            ax_object_class_mock.is_dead = self.mocker.Mock(return_value=False)
            ax_object_class_mock.get_name = self.mocker.Mock(return_value="")
            ax_object_class_mock.get_role = self.mocker.Mock(return_value=Atspi.Role.PANEL)
            ax_object_class_mock.get_parent = self.mocker.Mock(return_value=None)
            ax_object_class_mock.find_ancestor = self.mocker.Mock(return_value=None)
            ax_object_class_mock.clear_cache = self.mocker.Mock()
            ax_object_mock.AXObject = ax_object_class_mock

        if "blind_x.ax_utilities" in essential_modules:
            ax_utilities_mock = essential_modules["blind_x.ax_utilities"]
            ax_utilities_class_mock = self.mocker.Mock()
            ax_utilities_class_mock.is_focused = self.mocker.Mock(return_value=True)
            ax_utilities_class_mock.is_table_cell_or_header = self.mocker.Mock(return_value=False)
            ax_utilities_class_mock.is_list_item = self.mocker.Mock(return_value=False)
            ax_utilities_class_mock.is_layout_only = self.mocker.Mock(return_value=False)
            ax_utilities_class_mock.get_status_bar = self.mocker.Mock(return_value=None)
            ax_utilities_class_mock.get_info_bar = self.mocker.Mock(return_value=None)
            ax_utilities_class_mock.is_showing = self.mocker.Mock(return_value=True)
            ax_utilities_class_mock.is_visible = self.mocker.Mock(return_value=True)
            ax_utilities_class_mock.is_sensitive = self.mocker.Mock(return_value=True)
            ax_utilities_mock.AXUtilities = ax_utilities_class_mock

        if "blind_x.input_event" in essential_modules:
            input_event_mock = essential_modules["blind_x.input_event"]
            input_event_mock.KEY_PRESSED_EVENT = "key-pressed"
            input_event_mock.KEY_RELEASED_EVENT = "key-released"
            input_event_mock.MOUSE_BUTTON_CLICKED_EVENT = "mouse-clicked"

        if "blind_x.orca_platform" in essential_modules:
            orca_platform_mock = essential_modules["blind_x.orca_platform"]
            orca_platform_mock.tablesdir = "/usr/share/liblouis/tables"

        if "blind_x.braille_presenter" in essential_modules:
            braille_presenter_mock = essential_modules["blind_x.braille_presenter"]
            presenter_instance = self.mocker.Mock()
            presenter_instance.use_braille = self.mocker.Mock(return_value=False)
            presenter_instance.get_braille_is_enabled = self.mocker.Mock(return_value=False)
            presenter_instance.get_flash_messages_are_enabled = self.mocker.Mock(return_value=False)
            presenter_instance.get_flash_messages_are_detailed = self.mocker.Mock(
                return_value=False,
            )
            presenter_instance.get_flashtime_from_settings = self.mocker.Mock(return_value=5000)
            braille_presenter_mock.get_presenter = self.mocker.Mock(return_value=presenter_instance)

        if "blind_x.presentation_manager" in essential_modules:
            presentation_manager_mock = essential_modules["blind_x.presentation_manager"]
            manager_instance = self.mocker.Mock()
            manager_instance.interrupt_presentation = self.mocker.Mock()
            manager_instance.present_message = self.mocker.Mock()
            manager_instance.speak_message = self.mocker.Mock()
            manager_instance.speak_character = self.mocker.Mock()
            manager_instance.present_braille_message = self.mocker.Mock()
            manager_instance.spell_item = self.mocker.Mock()
            manager_instance.spell_phonetically = self.mocker.Mock()
            manager_instance.play_sound = self.mocker.Mock()
            manager_instance.speak_contents = self.mocker.Mock()
            manager_instance.display_contents = self.mocker.Mock()
            presentation_manager_mock.get_manager = self.mocker.Mock(return_value=manager_instance)

        if "gi.repository" in essential_modules:
            gi_repo_mock = essential_modules["gi.repository"]
            gi_repo_mock.Gio = Gio
            gi_repo_mock.GLib = GLib

    def get_mock(self, name: str) -> MagicMock | None:
        """Returns mock object if it exists, None otherwise."""

        return self.mocks.get(name)

    def __enter__(self) -> BlindXTestContext:  # noqa: PYI034
        """Enter the test context."""

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the test context and clean up all patches."""

        for patch_obj in self.patches.values():
            patch_obj.stop()

        self.patches.clear()
        self.mocks.clear()
