from viren import get_names
from viren import do_rename
from viren import VirenError

import nose
import os
import tempfile


def make_fs(fs):
    """
    Create a testing FS in a temp dir, return path to dir.

    FS is given as a list of (filename, contents) tuples.
    """
    dir_path = tempfile.mkdtemp(prefix='viren-test-')
    for filename, contents in fs:
        path = os.path.join(dir_path, filename)
        open(path, 'w').write(contents)
    return dir_path


def read_fs(dir_path):
    """
    Read files in dir_path.

    Return FS as list of (filename, contents) tuples, where the filenames are
    in sorted order.
    """
    fs = []
    for name in os.listdir(dir_path):
        path = os.path.join(dir_path, name)
        fs.append((name, open(path).read()))
    fs.sort()
    return fs


def remove_fs(dir_path):
    """
    Remove files in dir_path and then the directory itself.
    """
    for name in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, name))
    os.rmdir(dir_path)


def check_success(old_fs, new_fs, old_names, new_names):
    """
    Create old_fs, rename old_names -> new_names, compare with new_fs.

    Expects the rename to succeed; raises an error otherwise.
    """
    dir_path = make_fs(old_fs)
    got_old_names = get_names(dir_path)
    nose.tools.assert_equal(got_old_names, old_names)
    do_rename(dir_path, new_names)
    got_new_fs = read_fs(dir_path)
    nose.tools.assert_equal(got_new_fs, new_fs)
    remove_fs(dir_path)


def check_failure(old_fs, new_fs, old_names, new_names, message):
    """
    Create old_fs, rename old_names -> new_names, compare with new_fs.

    Expects the rename to fail with an error containing message.
    """
    dir_path = make_fs(old_fs)
    got_old_names = get_names(dir_path)
    nose.tools.assert_equal(got_old_names, old_names)
    with nose.tools.assert_raises(VirenError) as cm:
        do_rename(dir_path, new_names)
    nose.tools.assert_in(message, cm.exception.message)
    got_new_fs = read_fs(dir_path)
    nose.tools.assert_equal(got_new_fs, new_fs)
    remove_fs(dir_path)


def test_simple():
    """
    Simple rename works.
    """
    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('aa', '1'), ('bb', '2'), ('cc', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['aa', 'bb', 'cc']
    check_success(old_fs, new_fs, old_names, new_names)


def test_loop():
    """
    Renaming files in a loop works.
    """
    old_fs = [('a', '1'), ('b', '2'), ('c', '3'), ('d', '4')]
    new_fs = [('a', '4'), ('b', '1'), ('c', '2'), ('d', '3')]
    old_names = ['a', 'b', 'c', 'd']
    new_names = ['b', 'c', 'd', 'a']
    check_success(old_fs, new_fs, old_names, new_names)


def test_spaces():
    """
    Spaces in file names are OK.
    """
    old_fs = [('a', '1'), ('a a', '2'), ('a a a', '3')]
    new_fs = [('b b', '1'), ('c', '2'), ('d d d', '3')]
    old_names = ['a', 'a a', 'a a a']
    new_names = ['b b', 'c', 'd d d']
    check_success(old_fs, new_fs, old_names, new_names)


def test_spaces_on_edge():
    """
    Spaces at the beginning or end of a filename are ignored.
    """
    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('aa', '1'), ('bb', '2'), ('cc', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['aa  ', '   bb', '  cc   ']
    check_success(old_fs, new_fs, old_names, new_names)


def test_slashes():
    """
    Slashes in filenames are not allowed.
    """
    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['a/a', 'bb', 'cc']
    check_failure(old_fs, new_fs, old_names, new_names, "slash")


def test_mismatch():
    """
    Fails if too many or too few names provided.
    """
    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['aa', 'bb', 'cc', 'dd']
    check_failure(old_fs, new_fs, old_names, new_names, "list has")

    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['aa', 'bb']
    check_failure(old_fs, new_fs, old_names, new_names, "list has")


def test_collision():
    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['aa', 'aa', 'cc']
    check_failure(old_fs, new_fs, old_names, new_names, "duplicate")


def test_dots():
    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['aa', 'bb', '.']
    check_failure(old_fs, new_fs, old_names, new_names, ". or ..")

    old_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    new_fs = [('a', '1'), ('b', '2'), ('c', '3')]
    old_names = ['a', 'b', 'c']
    new_names = ['aa', '..', 'cc']
    check_failure(old_fs, new_fs, old_names, new_names, ". or ..")


# TODO:
# - unit tests for mk_temp_subdir
# - unit tests for verify_rename_list instead of only end-to-end tests
# - handles hidden files
# - noop if file not edited
