# Blind-X Screen Reader (based on Orca v51.alpha)

[TOC]

## Attention Application Developers

If you are an application developer trying to make your application work with Blind-X, please see the
[README for application developers](docs/application-developers.md).

## Introduction

Blind-X is a free, open source, flexible, and extensible screen reader
that provides access to the graphical desktop via user-customizable
combinations of speech and/or braille. It is based on the GNOME Orca
screen reader.

Blind-X works with applications and toolkits that support the assistive
technology service provider interface (AT-SPI), which is the primary
assistive technology infrastructure for Solaris and Linux.

See <https://github.com/jhonata192/blind-x-screen-reader> for detailed information on the
upstream Orca project.

## Dependencies

Blind-X has the following dependencies:

* meson: The build system used by Blind-X
* Python 3: Python platform
* pygobject-3.0: Python bindings for the GObject library
* gtk+-3.0: GTK+ toolkit
* python3-babel: Babel support for localized language display names (optional)
* python3-brlapi: BrlAPI (<https://mielke.cc/brltty/>) support for braille (optional)
* python3-dasbus: Dasbus (<https://dasbus.readthedocs.io/>) support for remote control of Blind-X
* python3-louis: Liblouis (<https://liblouis.io/>) support for contracted braille (optional)
* python3-psutil: Process and system utilities (optional)
* python3-setproctitle: Python library to set the process title (optional)
* python3-speechd: Python bindings for Speech Dispatcher (optional)
* gstreamer-1.0: GStreamer - Streaming media framework (optional)
* libwnck3: Used for mouse review in X11 (optional, deprecated)

You are strongly encouraged to also have the latest stable versions
of AT-SPI2 and ATK for the GNOME 50.x release.

## Note for Braille Users

You can determine if the Python bindings for BrlAPI are installed by running the following command:

```sh
python -c "import brlapi"
```

If you get an error, the Python bindings for BrlAPI are not installed.

## Building and Installing Blind-X

If you want to build Blind-X in a directory called `_build` and install Blind-X using
your distro's default location (e.g `/usr/local`):

```sh
meson setup _build
meson compile -C _build
meson install -C _build
```

The installer will prompt you for `sudo` permission if needed.

To specify an alternative install location, use `-D prefix=` during setup
(e.g. `meson setup -D prefix=$HOME/orca-test _build`).

To rebuild, either remove the build directory you created before (e.g. `_build`)
or add the `--reconfigure` flag to the end of your existing `meson setup` command.

To uninstall, `cd` into the build directory you created and use `ninja uninstall`,
or `sudo ninja uninstall` if you had installed Orca with `sudo` permission.
Note that this will not remove the bytecode files in `__pycache__`. See this
[meson issue](https://github.com/mesonbuild/meson/issues/12798).

## Running Blind-X

If you wish to modify your Blind-X preferences, you can press "Insert+space"
while Blind-X is running.

To get help while running Blind-X, press "Insert+H".  This will enable
"learn mode", which provides a spoken and brailled description of what
various keyboard and braille input device actions will do.

## Blind-X's Scripts and Features

Blind-X's scripts provide access to applications and toolkits by responding to
accessible events. For instance, when focus changes in an application, that
application will emit an accessible event, `object:state-changed:focused`,
which is then handled by the script associated with the application or toolkit.

If you have an application or toolkit that is accessible, but poorly supported
by Blind-X, writing a custom script for that application might be the correct
solution. To see examples of scripts, look in `src/blind_x/scripts` of the
source tree.

Scripts can also import features, but the features themselves do not live inside the script;
they live in navigators, presenters, and other such modules.

## Remote Controller (D-Bus Interface)

Blind-X provides a D-Bus interface that allows external applications to remotely control Blind-X's
functionality and present messages to users. For detailed usage instructions, examples, and
API documentation, see [remote-controller.md](docs/remote-controller.md).

## GSettings Support

Blind-X uses GSettings for its configuration. A list of Blind-X's
schemas, keys, defaults, and enums is available in [gsettings-schemas.md](docs/gsettings-schemas.md).

## Spiel Text-to-Speech Support

By default, Blind-X uses speech-dispatcher for its TTS support. There is also basic support for
[Spiel](https://github.com/project-spiel) which allows choosing voices from multiple synthesizers,
currently including eSpeak and Piper.

To test Spiel, configure Blind-X to build from the latest source. Once compiled,
`meson devenv` will be used to run Blind-X.

```sh
meson setup --force-fallback-for=spiel -Dspiel=true _build
meson compile -C _build
meson install -C _build
```

If you have an existing build directory, don't forget to use `--reconfigure`. If
you have problems after an update, you may need to re-build and re-install:

```sh
meson subprojects purge --confirm
meson setup --reconfigure --force-fallback-for=spiel -Dspiel=true _build 
meson compile --clean -C _build
meson install -C _build

# Ensure any old Spiel providers get restarted
flatpak kill ai.piper.Speech.Provider
flatpak kill org.espeak.Speech.Provider
```

Then install the Flatpak for one or more speech providers (i.e. piper or speak) by running the
commands in the [Spiel documentation](https://project-spiel.org/install.html)

To switch from Speech Dispatcher to Spiel, use `blind-x --replace --speech-system=spiel`. Using
this flag is highly recommended while Blind-X's Spiel support is experimental. If you would like
to use Spiel by default, you can select it in Blind-X's Preferences dialog. To then switch back
to Speech Dispatcher, use `blind-x --replace --speech-system=speechdispatcherfactory`.

```sh
# Enter the development environment
meson devenv -C _build

# Run Blind-X
blind-x --replace --speech-system=spiel

# Exit the development environment
exit
```

### Building Spiel from Source

For advanced users, Spiel and providers may be built from source. If you are
unsure, consider using the available Flatpaks and consult the documentation for
your distribution before proceeding.

1. Build and install Blind-X with Spiel

   Be sure to build Blind-X as described above, so the correct `libspeechprovider`
   version is available when building a provider in the next step. If you
   previously built Blind-X, follow the steps to update and re-build before
   continuing.

2. Next build and install a provider

   ```sh
   # Clone the repository, then select a provider in the "providers/" directory
   git clone https://github.com/eeejay/spiel-demos.git
   cd spiel-demos/providers/espeak

   # Build and install
   meson setup _build
   meson compile -C _build
   meson install -C _build
   ```

Now start Blind-X following the [instructions](#spiel-text-to-speech-support) above and
the Spiel providers you installed will start automatically.
