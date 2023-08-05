#!/usr/bin/env python3

import os.path
import zipfile
import argparse
import os
import shutil

program_version = 1.0

def get_args():
    '''get command line args'''
    parser = argparse.ArgumentParser(
            description = 'Assign some comic dirs and archive to .cbz format.')
    parser.add_argument('folders', metavar = 'COMICDIR',
            type = str, nargs = '*',
            help = 'Comic book container. It should include multiple volume dirs.')
    parser.add_argument('-k', '--keep-vol-dir', dest = 'keep_vol_dir',
            action = 'store_const', const = True, default = False,
            help = 'Let the "volume dir" not be deleted.')
    parser.add_argument('-v', '--version', action = 'version',
            version = str(program_version))

    args = parser.parse_args()
    return args

def archive_cbz(folder):
    '''zip the folder to .cbz format in the folder's parent dir
    '''
    if os.path.isdir(folder):
        basename = os.path.basename(folder)
        filename = basename + '.cbz'
        dirname = os.path.dirname(folder)
        filepath = os.path.join(dirname, filename)
        with zipfile.ZipFile(filepath, 'w') as zfile:
            for path, dirs, files in os.walk(folder):
                for fn in files:
                    absfn = os.path.join(path, fn)
                    zfn = os.path.relpath(absfn, dirname)
                    zfile.write(absfn, zfn)
        print('Archive OK: ' + filepath)
    else:
        raise RuntimeError(
                'folder: "{}" Not a dir! do nothing'.format(folder))

def main():
    '''entry point'''
    args = get_args()

    # walk all folders
    for folder in args.folders:
        isdir = os.path.isdir(folder)
        if isdir:
            subdirs = [ os.path.join(folder, subdir) for subdir
                    in os.listdir(folder)
                    if os.path.isdir(os.path.join(folder, subdir)) ]
            for subdir in subdirs:
                try:
                    archive_cbz(subdir)
                    if not args.keep_vol_dir:
                        shutil.rmtree(subdir)
                except RuntimeError as e:
                    print(e)

if __name__ == '__main__':
    main()
