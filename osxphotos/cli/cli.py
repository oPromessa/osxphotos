"""Command line interface for osxphotos"""

import atexit
import cProfile
import io
import pstats
import sys

import click

from osxphotos._constants import PROFILE_SORT_KEYS
from osxphotos.disclaim import disclaim, pyapp, pyinstaller
from osxphotos.platform import is_macos

from .about import about
from .albums import albums
from .cli_params import DEBUG_OPTIONS, VERSION_OPTION
from .common import OSXPHOTOS_HIDDEN
from .compare import compare
from .debug_dump import debug_dump
from .docs import docs_command
from .dump import dump
from .exiftool_cli import exiftool
from .export import export
from .exportdb import exportdb
from .grep import grep
from .help import help
from .info import info
from .install_uninstall_run import install, run, uninstall
from .keywords import keywords
from .labels import labels
from .list import list_libraries
from .orphans import orphans
from .persons import persons
from .places import places
from .query import query
from .repl import repl
from .snap_diff import diff, snap
from .template_repl import template_repl
from .theme import theme
from .tutorial import tutorial
from .update_command import update_command
from .version import version

if is_macos:
    from .add_locations import add_locations
    from .batch_edit import batch_edit
    from .import_cli import import_main
    from .photo_inspect import photo_inspect
    from .push_exif import push_exif
    from .show_command import show
    from .sync import sync
    from .timewarp import timewarp
    from .uuid import uuid


# Click CLI object & context settings
class CLI_Obj:
    def __init__(self, db=None, json=False, debug=False, group=None):
        self.db = db
        self.json = json
        self.group = group


CTX_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CTX_SETTINGS)
@VERSION_OPTION
@DEBUG_OPTIONS
@click.option(
    "--profile", is_flag=True, hidden=OSXPHOTOS_HIDDEN, help="Enable profiling"
)
@click.option(
    "--profile-sort",
    default=None,
    hidden=OSXPHOTOS_HIDDEN,
    multiple=True,
    metavar="SORT_KEY",
    type=click.Choice(
        PROFILE_SORT_KEYS,
        case_sensitive=True,
    ),
    help="Sort profiler output by SORT_KEY as specified at https://docs.python.org/3/library/profile.html#pstats.Stats.sort_stats. "
    f"Can be specified multiple times. Valid options are: {PROFILE_SORT_KEYS}. "
    "Default = 'cumulative'.",
)
@click.pass_context
def cli_main(ctx, profile, profile_sort, **kwargs):
    """OSXPhotos: the multi-tool for your Photos library.

    To get help on a specific command, use "osxphotos COMMAND --help"
    or "osxphotos help COMMAND"; for example, "osxphotos help export".

    To search help for a specific topic within a command, run
    "osxphotos help COMMAND TOPIC"; for example,
    "osxphotos help export keyword" to get help related to keywords
    when using the export command.

    To see the full documentation in your browser, run "osxphotos docs".

    Some advanced commands are hidden by default. To see all commands,
    run "OSXPHOTOS_SHOW_HIDDEN=1 osxphotos help". Some commands also have
    hidden options. These can be seen by running
    "OSXPHOTOS_SHOW_HIDDEN=1 osxphotos help COMMAND".
    """
    # Note: kwargs is used to catch any debug options passed in
    # the debug options are handled in cli/__init__.py
    # before this function is called
    ctx.obj = CLI_Obj(group=cli_main)

    if pyinstaller() or pyapp():
        # Running from executable, run disclaimer
        disclaim()

    if profile:
        click.echo("Profiling...")
        profile_sort = profile_sort or ["cumulative"]
        click.echo(f"Profile sort_stats order: {profile_sort}")
        pr = cProfile.Profile()
        pr.enable()

        def at_exit():
            pr.disable()
            click.echo("Profiling completed")
            s = io.StringIO()
            pstats.Stats(pr, stream=s).strip_dirs().sort_stats(
                *profile_sort
            ).print_stats()
            click.echo(s.getvalue())

        atexit.register(at_exit)

    def flush_stderr():
        # click CliRunner doesn't respect line buffered stderr so flush it manually
        # this is only needed for testing
        sys.stderr.flush()

    atexit.register(flush_stderr)


# install CLI commands
commands = [
    about,
    albums,
    compare,
    debug_dump,
    diff,
    docs_command,
    dump,
    exiftool,
    export,
    exportdb,
    grep,
    help,
    info,
    install,
    keywords,
    labels,
    list_libraries,
    orphans,
    persons,
    places,
    query,
    repl,
    run,
    snap,
    theme,
    tutorial,
    template_repl,
    uninstall,
    version,
    update_command,
]

if is_macos:
    commands += [
        add_locations,
        batch_edit,
        import_main,
        photo_inspect,
        push_exif,
        show,
        sync,
        timewarp,
        uuid,
    ]

for command in commands:
    cli_main.add_command(command)
