#!/usr/bin/python
from subprocess import Popen, PIPE
import argh
import ast
import os


def _execute(command):

    # Run the command
    process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)

    std_out, std_err = process.communicate()
    return_code = process.returncode

    return (std_out, std_err, return_code)


def reset_wifi():
    _execute("sudo service network-manager stop")
    _execute("sudo rm -f /var/lib/NetworkManager/NetworkManager.state")
    _execute("sudo service network-manager start")


@argh.arg(
    'location', nargs=1, choices=['user', 'system', 'all'])
def list_extensions(location):
    print "\n".join(get_extensions(location))


def get_extensions(location):
    location = location[0]
    extensions = []
    if location in ['user', 'all']:
        path = os.path.expanduser('~/.local/share/gnome-shell/extensions')
        elist = os.listdir(path)
        extensions.extend(elist)
    if location in ['system', 'all']:
        path = os.path.expanduser('/usr/share/gnome-shell/extensions')
        elist = os.listdir(path)
        extensions.extend(elist)
    return extensions


@argh.arg(
    'location', nargs=1, default='all', choices=['user', 'system', 'all'])
def list_enabled_extensions(location):
    default_extensions = {}
    default_extensions['user'] = get_extensions(['user'])
    default_extensions['system'] = get_extensions(['system'])
    default_extensions['all'] = get_extensions(['all'])
    extensions = get_enabled_extensions()
    extensions = [
        e for e in extensions if e in default_extensions[location[0]]]

    print '\n'.join(extensions)


def get_enabled_extensions():
    std_out, _, _ = _execute(
        'gsettings get org.gnome.shell enabled-extensions')
    try:
        return ast.literal_eval(std_out)
    except:
        return []


ext = ['user', 'system', 'all']
ext.extend(get_extensions(['all']))
extension_decorator = argh.arg(
    'extensions', nargs="+", choices=ext, metavar='',
    help="run the list-extensions command to see a list of available"
         " extensions")


def _expand_requested_extension_list(extensions):
    default_extensions = {}
    default_extensions['user'] = get_extensions(['user'])
    default_extensions['system'] = get_extensions(['system'])
    default_extensions['all'] = get_extensions(['all'])
    final_extension_list = []
    for metatype in ['user', 'system', 'all']:
        if metatype in extensions:
            try:
                while True:
                    extensions.remove(metatype)
            except:
                pass
            final_extension_list.extend(default_extensions[metatype])
    final_extension_list.extend(extensions)
    return final_extension_list


@extension_decorator
def enable_extensions(extensions):
    extensions = _expand_requested_extension_list(extensions)
    extensions.extend(get_enabled_extensions())

    _execute(
        'gsettings set org.gnome.shell enabled-extensions '
        '"{0}"'.format(extensions))


@extension_decorator
def disable_extensions(extensions):
    extensions = _expand_requested_extension_list(extensions)
    enabled_extensions = get_enabled_extensions()

    extensions = [e for e in enabled_extensions if e not in extensions]
    _execute(
        'gsettings set org.gnome.shell enabled-extensions '
        '"{0}"'.format(extensions))


def reset_extensions():
    extensions = get_enabled_extensions()
    _execute(
        'gsettings set org.gnome.shell enabled-extensions '
        '"{0}"'.format(extensions))


def get_display_list():
    std_out, _, _ = _execute('xrandr')
    std_out = std_out.splitlines()
    displays = [
        line.split()[0] for line in std_out if (
            not line.startswith(' ') and not line.startswith('Screen'))]
    return displays


def list_displays():
    print '\n'.join(get_display_list())


display_choices = get_display_list()
display_choices.extend(['all'])


@argh.arg(
    'displays', nargs="+", choices=display_choices, metavar='',
    help="You can choose 'all', or any number of displays from the "
    "list-displays command")
def fix_colors(displays):
    for display in displays:
        _execute(
            'xrandr --output {display} --set "Broadcast RGB" "Full"'.format(
                display=display))


@argh.arg('factor', type=float)
def scale_gui(factor):
    return _execute(
        'gsettings set org.gnome.desktop.interface text-scaling-factor '
        '{factor}'.format(factor=factor))


parser = argh.ArghParser()
parser.add_commands(
    [list_extensions,
     list_enabled_extensions,
     enable_extensions,
     disable_extensions,
     reset_extensions,
     fix_colors,
     scale_gui,
     list_displays,
     reset_wifi])

if __name__ == "__main__":
    parser.dispatch()


def entry_point():
    parser.dispatch()
