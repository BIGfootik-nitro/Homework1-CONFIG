import pytest
from terminal import MyTerminal
import tarfile


@pytest.fixture
def terminal():
    user_name = 'test_user'
    fs_path = 'archive.tar'
    tarfile.open(fs_path)
    log_file = 'logs.json'
    start_script = 'start.txt'
    t = MyTerminal(user_name, fs_path, log_file, start_script)
    return t


@pytest.mark.parametrize(
    'arg, expected', [
        ([],
         '''desktop
hello.txt
users
'''),
        (['desktop'],
         '''folder
more_textes.txt
'''),
        (['users'],
         '''root
user
''')
    ]
)
def test_ls(terminal, arg, expected):
    val = terminal.ls(arg)
    assert val == expected


@pytest.mark.parametrize(
    'arg, expected', [
        ([],
         'root directory'),
        (['desktop'],
         'change to desktop'),
        (['users'],
         'change to users')
    ]
)
def test_cd(terminal, arg, expected):
    val = terminal.cd(arg)
    assert val == expected
