schema_generator = files('../tools/generate_gsettings_schemas.py')

# Source files with @gsettings_schema decorators. For meson dependency tracking only;
# the Python script discovers schemas by scanning src/blind_x/*.py at build time.
schema_sources = files(
  '../src/blind_x/speechserver.py',
  '../src/blind_x/speech_manager.py',
  '../src/blind_x/speech_presenter.py',
  '../src/blind_x/braille_presenter.py',
  '../src/blind_x/typing_echo_presenter.py',
  '../src/blind_x/caret_navigator.py',
  '../src/blind_x/structural_navigator.py',
  '../src/blind_x/table_navigator.py',
  '../src/blind_x/document_presenter.py',
  '../src/blind_x/say_all_presenter.py',
  '../src/blind_x/flat_review_presenter.py',
  '../src/blind_x/sound_presenter.py',
  '../src/blind_x/chat_presenter.py',
  '../src/blind_x/spellcheck_presenter.py',
  '../src/blind_x/mouse_review.py',
  '../src/blind_x/live_region_presenter.py',
  '../src/blind_x/math_presenter.py',
  '../src/blind_x/system_information_presenter.py',
  '../src/blind_x/pronunciation_dictionary_manager.py',
  '../src/blind_x/command_manager.py',
  '../src/blind_x/text_attribute_manager.py',
  '../src/blind_x/profile_manager.py',
  '../src/blind_x/blind_x_modifier_manager.py',
  '../src/blind_x/sleep_mode_manager.py',
  '../src/blind_x/extension_loader.py',
)

generated_schema = custom_target(
  'org.gnome.BlindX.gschema.xml',
  output: 'org.gnome.BlindX.gschema.xml',
  command: [python3, schema_generator, meson.project_source_root() / 'src', '@OUTPUT@'],
  depend_files: [schema_generator, schema_sources],
  install: true,
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

glib_compile_schemas = find_program('glib-compile-schemas', required: false)
if glib_compile_schemas.found()
  validate_schemas_cmd = '; '.join([
    'import pathlib, subprocess, sys',
    'subprocess.check_call([sys.argv[1], "--strict", "--dry-run", sys.argv[2]])',
    'pathlib.Path(sys.argv[3]).write_text("ok")',
  ])
  test(
    'validate-schemas',
    glib_compile_schemas,
    args: ['--strict', '--dry-run', meson.current_build_dir()],
    depends: generated_schema,
  )
  custom_target(
    'validate-schemas-build',
    output: 'schemas.validated',
    command: [
      python3,
      '-c',
      validate_schemas_cmd,
      glib_compile_schemas,
      meson.current_build_dir(),
      '@OUTPUT@',
    ],
    depends: generated_schema,
    build_by_default: true,
  )
endif
