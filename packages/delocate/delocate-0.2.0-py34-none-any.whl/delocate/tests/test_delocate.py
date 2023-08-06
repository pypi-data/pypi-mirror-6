""" Tests for relocating libraries """

from __future__ import division, print_function

import os
from os.path import (join as pjoin, dirname, basename, relpath, realpath)
import shutil

from ..delocator import (DelocationError, delocate_tree_libs, copy_recurse,
                         delocate_path)
from ..tools import (tree_libs, get_install_names, get_rpaths,
                     set_install_name, back_tick)

from ..tmpdirs import InTemporaryDirectory

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)

from .test_install_names import (DATA_PATH, LIBA, LIBB, LIBC, TEST_LIB,
                                 _copy_libs)

# External libs linked from test data
EXT_LIBS = ('/usr/lib/libstdc++.6.dylib', '/usr/lib/libSystem.B.dylib')

def _make_libtree(out_path):
    liba, libb, libc, test_lib = _copy_libs(
        [LIBA, LIBB, LIBC, TEST_LIB], out_path)
    sub_path = pjoin(out_path, 'subsub')
    slibc, stest_lib = _copy_libs([libc, test_lib], sub_path)
    # Set execute permissions
    for exe in (test_lib, stest_lib):
        os.chmod(exe, 0o744)
    # Check test-lib doesn't work because of relative library paths
    assert_raises(RuntimeError, back_tick, [test_lib])
    assert_raises(RuntimeError, back_tick, [stest_lib])
    # Fixup the relative path library names by setting absolute paths
    for fname, using, path in (
        (libb, 'liba.dylib', out_path),
        (libc, 'liba.dylib', out_path),
        (libc, 'libb.dylib', out_path),
        (test_lib, 'libc.dylib', out_path),
        (slibc, 'liba.dylib', out_path),
        (slibc, 'libb.dylib', out_path),
        (stest_lib, 'libc.dylib', sub_path),
                        ):
        set_install_name(fname, using, pjoin(path, using))
    # Check scripts now execute correctly
    back_tick([test_lib])
    back_tick([stest_lib])
    return liba, libb, libc, test_lib, slibc, stest_lib


def test_delocate_tree_libs():
    # Test routine to copy library dependencies into a local directory
    with InTemporaryDirectory() as tmpdir:
        # Copy libs into a temporary directory
        subtree = pjoin(tmpdir, 'subtree')
        all_local_libs = _make_libtree(subtree)
        liba, libb, libc, test_lib, slibc, stest_lib = all_local_libs
        lib_dict = tree_libs(subtree)
        copy_dir = 'dynlibs'
        os.makedirs(copy_dir)
        # First check that missing library causes error
        set_install_name(liba,
                         '/usr/lib/libstdc++.6.dylib',
                         '/unlikely/libname.dylib')
        lib_dict = tree_libs(subtree)
        assert_raises(DelocationError,
                      delocate_tree_libs, lib_dict, copy_dir, subtree)
        # fix - it works
        set_install_name(liba,
                         '/unlikely/libname.dylib',
                         '/usr/lib/libstdc++.6.dylib')
        lib_dict = tree_libs(subtree)
        copied = delocate_tree_libs(lib_dict, copy_dir, subtree)
        # Only the out-of-tree libraries get copied
        assert_equal(copied, set(EXT_LIBS))
        assert_equal(set(os.listdir(copy_dir)),
                     set([basename(lib) for lib in EXT_LIBS]))
        # Libraries using the copied libraries now have an rpath pointing to
        # the copied library directory, and rpath/libname as install names
        to_exts = set(['@rpath/' + basename(elib) for elib in copied])
        for lib in all_local_libs:
            pathto_copies = relpath(copy_dir, dirname(lib))
            assert_equal(get_rpaths(lib), ('@loader_path/' + pathto_copies,))
            assert_true(to_exts <= set(get_install_names(lib)))
        # Libraries now have a relative loader_path to their corresponding
        # in-tree libraries
        for requiring, using, rel_path in (
            (libb, 'liba.dylib', ''),
            (libc, 'liba.dylib', ''),
            (libc, 'libb.dylib', ''),
            (test_lib, 'libc.dylib', ''),
            (slibc, 'liba.dylib', '../'),
            (slibc, 'libb.dylib', '../'),
            (stest_lib, 'libc.dylib', '')):
            loader_path = '@loader_path/' + rel_path + using
            assert_true(loader_path in get_install_names(requiring))
        # Check test libs still work
        back_tick([test_lib])
        back_tick([stest_lib])
        # Check case where all local libraries are out of tree
        subtree2 = pjoin(tmpdir, 'subtree2')
        liba, libb, libc, test_lib, slibc, stest_lib = _make_libtree(subtree2)
        copy_dir2 = 'dynlibs2'
        os.makedirs(copy_dir2)
        # Trying to delocate where all local libraries appear to be
        # out-of-tree will raise an error because of duplicate library names
        lib_dict2 = tree_libs(subtree2)
        assert_raises(DelocationError,
                      delocate_tree_libs, lib_dict2, copy_dir2, '/tmp')
        # Rename a library to make this work
        new_slibc = pjoin(dirname(slibc), 'libc2.dylib')
        os.rename(slibc, new_slibc)
        # Tell test-lib about this
        set_install_name(stest_lib, slibc, new_slibc)
        slibc = new_slibc
        # Confirm new test-lib still works
        back_tick([test_lib])
        back_tick([stest_lib])
        # Delocation now works
        lib_dict2 = tree_libs(subtree2)
        copied2 = delocate_tree_libs(lib_dict2, copy_dir2, '/tmp')
        ext_local_libs = set(EXT_LIBS) | set([liba, libb, libc, slibc])
        assert_equal(copied2, ext_local_libs)
        assert_equal(set(os.listdir(copy_dir2)),
                     set([basename(lib) for lib in ext_local_libs]))
        # Libraries using the copied libraries now have an rpath pointing to
        # the copied library directory, and rpath/libname as install names
        all_local_libs = liba, libb, libc, test_lib, slibc, stest_lib
        for lib in all_local_libs:
            pathto_copies = relpath(copy_dir2, dirname(lib))
            assert_equal(get_rpaths(lib), ('@loader_path/' + pathto_copies,))
            assert_true(to_exts <= set(get_install_names(lib)))


def _copy_fixpath(files, directory):
    new_fnames = []
    for fname in files:
        shutil.copy2(fname, directory)
        new_fname = pjoin(directory, basename(fname))
        for name in get_install_names(fname):
            if name.startswith('lib'):
                set_install_name(new_fname, name, pjoin(directory, name))
        new_fnames.append(new_fname)
    return new_fnames


def _copy_to(fname, directory, new_base):
    new_name = pjoin(directory, new_base)
    shutil.copy2(fname, new_name)
    return new_name


def test_copy_recurse():
    # Function to find / copy needed libraries recursively
    with InTemporaryDirectory():
        # Get some fixed up libraries to play with
        os.makedirs('libcopy')
        test_lib, liba, libb, libc = _copy_fixpath(
            [TEST_LIB, LIBA, LIBB, LIBC], 'libcopy')
        # Set execute permissions
        os.chmod(test_lib, 0o744)
        # Check system finds libraries
        back_tick(['./libcopy/test-lib'])
        # One library, system filtered
        def filt_func(libname):
            return not libname.startswith('/usr/lib')
        os.makedirs('subtree')
        _copy_fixpath([LIBA], 'subtree')
        assert_equal(copy_recurse('subtree', copy_filt_func=filt_func),
                     set())
        assert_equal(set(os.listdir('subtree')), set(['liba.dylib']))
        # An object that depends on a library that depends on two libraries
        os.makedirs('subtree2')
        shutil.copy2(test_lib, 'subtree2')
        assert_equal(copy_recurse('subtree2', filt_func),
                     set([liba, libb, libc]))
        assert_equal(set(os.listdir('subtree2')),
                     set(('liba.dylib',
                          'libb.dylib',
                          'libc.dylib',
                          'test-lib')))
        # A circular set of libraries
        os.makedirs('libcopy2')
        libw = _copy_to(LIBA, 'libcopy2', 'libw.dylib')
        libx = _copy_to(LIBA, 'libcopy2', 'libx.dylib')
        liby = _copy_to(LIBA, 'libcopy2', 'liby.dylib')
        libz = _copy_to(LIBA, 'libcopy2', 'libz.dylib')
        # targets and dependencies.  libw starts in the directory, first pass
        # should install libx and liby (dependencies of libw), second pass
        # should install libz
        t_dep1_dep2 = (
            (libw, libx, liby),
            (libx, libw, liby),
            (liby, libw, libz), # only liby depends on libz
            (libz, libw, libx))
        for tlib, dep1, dep2 in t_dep1_dep2:
            set_install_name(tlib, EXT_LIBS[0], dep1)
            set_install_name(tlib, EXT_LIBS[1], dep2)
        os.makedirs('subtree3')
        shutil.copy2(libw, 'subtree3')
        copy_recurse('subtree3') # not filtered
        assert_equal(set(os.listdir('subtree3')),
                     set(('libw.dylib',
                          'libx.dylib',
                          'liby.dylib',
                          'libz.dylib')))
        for tlib, dep1, dep2 in t_dep1_dep2:
            out_lib = pjoin('subtree3', basename(tlib))
            assert_equal(set(get_install_names(out_lib)),
                         set(('@loader_path/' + basename(dep1),
                              '@loader_path/' + basename(dep2))))



def test_delocate_path():
    # Test high-level path delocator script
    with InTemporaryDirectory():
        # Make a tree; use realpath for OSX /private/var - /var
        _, _, _, test_lib, slibc, stest_lib = _make_libtree(
            realpath('subtree'))
        # Check it fixes up correctly
        assert_equal(delocate_path('subtree', 'deplibs'),
                     set())
        assert_equal(len(os.listdir('deplibs')), 0)
        back_tick([test_lib])
        back_tick([stest_lib])
        # Make a fake external library to link to
        os.makedirs('fakelibs')
        fake_lib = realpath(_copy_to(LIBA, 'fakelibs', 'libfake.dylib'))
        _, _, _, test_lib, slibc, stest_lib = _make_libtree(
            realpath('subtree2'))
        set_install_name(slibc, EXT_LIBS[0], fake_lib)
        # Check fake libary gets copied and delocated
        assert_equal(delocate_path('subtree2', 'deplibs2'),
                     set([fake_lib]))
        assert_equal(os.listdir('deplibs2'), ['libfake.dylib'])
        assert_true('@rpath/libfake.dylib' in get_install_names(slibc))
        assert_true('@loader_path/../../deplibs2' in get_rpaths(slibc))
        # Unless we set the filter otherwise
        _, _, _, test_lib, slibc, stest_lib = _make_libtree(
            realpath('subtree3'))
        set_install_name(slibc, EXT_LIBS[0], fake_lib)
        def filt(libname):
            return not (libname.startswith('/usr') or
                        'libfake' in libname)
        assert_equal(delocate_path('subtree3', 'deplibs3', None, filt),
                     set())
        assert_equal(len(os.listdir('deplibs3')), 0)
        # Test tree names filtering works
        _, _, _, test_lib, slibc, stest_lib = _make_libtree(
            realpath('subtree4'))
        set_install_name(slibc, EXT_LIBS[0], fake_lib)
        def lib_filt(filename):
            return not filename.endswith('subsub/libc.dylib')
        assert_equal(delocate_path('subtree4', 'deplibs4', lib_filt),
                     set())
        assert_equal(len(os.listdir('deplibs4')), 0)
        # Check can use already existing directory
        os.makedirs('deplibs5')
        _, _, _, test_lib, slibc, stest_lib = _make_libtree(
            realpath('subtree5'))
        assert_equal(delocate_path('subtree5', 'deplibs5'),
                     set())
        assert_equal(len(os.listdir('deplibs5')), 0)
