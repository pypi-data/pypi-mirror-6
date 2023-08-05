#!/usr/bin/env python

import os
import random
import subprocess
import sys
import tempfile


class VirenError(RuntimeError):
    pass


def verify_rename_list(old_names, new_names):
    """
    Sanity check a rename proposal.

    If there is a problem (new names not provided, or they collide among
    themselves, etc), raises VirenError.
    """
    if len(old_names) != len(new_names):
        raise VirenError("Edited list has {} names, expected {}".format(
            len(new_names), len(old_names)))
    seen_names = set()
    for lineno, name in enumerate(new_names, 1):
        if not name:
            raise VirenError("Line {}: empty filename".format(lineno))
        if '/' in name:
            raise VirenError("Line {}: slash in filename".format(lineno))
        if name in ('.', '..'):
            raise VirenError("Line {}: filename is . or ..".format(lineno))
        if name in seen_names:
            raise VirenError("Line {}: duplicate filename".format(lineno))
        seen_names.add(name)


def mk_temp_subdir(dir_path, forbidden_names):
    """
    Make a temp subdir in pwd and return its path.

    The directory name is assigned randomly, and checked not to collide with
    `forbidden_names`.
    """
    for attempt in xrange(10):
        name = 'viren-' + hex(random.randint(1e9, 1e10))[2:]
        path = os.path.join(dir_path, name)
        if name in forbidden_names or os.path.exists(path):
            continue
        os.mkdir(path)
        return path
    raise VirenError("Failed to create temp subdir")


def get_names(dir_path):
    """
    Return list of filenames in given dir, in sorted order.
    """
    names = os.listdir(dir_path)
    names.sort()
    return names


def do_rename(dir_path, new_names):
    """
    Rename files in dir_path (in sorted order) to new_names.

    Leading or trailing whitespace in `new_names` is ignored.

    Raises VirenError if the rename cannot be performed.
    """
    # Clean new_names and do some sanity checks.
    new_names = [name.strip() for name in new_names]
    old_names = get_names(dir_path)
    verify_rename_list(old_names, new_names)

    # Move the old files to a temp subdir. We do this to avoid accidental
    # overwrites, in case old_names and new_names overlap.
    subdir_path = mk_temp_subdir(dir_path, old_names + new_names)
    for name in old_names:
        old_path = os.path.join(dir_path, name)
        new_path = os.path.join(subdir_path, name)
        ret = subprocess.call(['mv', old_path, new_path])
        if ret != 0:
            raise VirenError('mv failed with return code {}'.format(ret))

    # Now move the files back with their new names.
    for i in xrange(len(old_names)):
        old_path = os.path.join(subdir_path, old_names[i])
        new_path = os.path.join(dir_path, new_names[i])
        ret = subprocess.call(['mv', old_path, new_path])
        if ret != 0:
            raise VirenError('mv failed with return code {}'.format(ret))

    # Clean up.
    os.rmdir(subdir_path)


def main():
    """
    Run viren in the current directory.
    """
    # Get sorted list of files in pwd.
    old_names = get_names('.')

    # Write that list to a temp file.
    _, temp_path = tempfile.mkstemp(prefix='viren-')
    temp = open(temp_path, 'w')
    temp.write('\n'.join(old_names))
    temp.close()

    try:
        # Let the user edit that file in her favorite editor.
        ret = subprocess.call(['editor', temp_path])
        if ret != 0:
            raise VirenError('editor failed with return code {}'.format(ret))

        # Get the edited list back from the temp file, and do the rename.
        new_names = [line.strip() for line in open(temp_path).xreadlines()]
        if new_names == old_names:
            print "No change."
        else:
            do_rename('.', new_names)
            print "Done renaming."

        # Clean up.
        os.remove(temp_path)

    except VirenError as err:
        print >>sys.stderr, "Something went wrong:"
        print >>sys.stderr, err.message
        print >>sys.stderr, "File list saved to {}".format(temp_path)
        sys.exit(1)


if __name__ == "__main__":
    main()
