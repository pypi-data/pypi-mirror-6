from __future__ import print_function
import argparse
import codecs
import sys
import os

import asstosrt


def _get_args():
    parser = argparse.ArgumentParser(description='A useful tool that \
                convert Advanced SubStation Alpha (ASS/SSA) subtitle files \
                to SubRip (SRT) subtitle files.',
            epilog='Auther: @xierch <sorz@sorz.org>; \
                bug report: https://github.com/bluen/asstosrt')
    parser.add_argument('-e', '--encoding', 
            help='charset of input ASS file (default: auto detect)')
    parser.add_argument('-t', '--translate-to', dest='language',
            help='set "zh-hans" for Simplified Chinese, \
                "zh-hant" for Traditional Chinese (need langconv)')
    parser.add_argument('-n', '--no-effact', action="store_true",
            help='ignore all effact text')
    parser.add_argument('-l', '--only-first-line', action="store_true",
            help='remove other lines on each dialogue')
    parser.add_argument('-s', '--srt-encoding', 
            help='charset of output SRT file (default: same as ASS)')
    parser.add_argument('-o', '--output-dir', default=os.getcwd(),
            help='output directory (default: current directory)')
    parser.add_argument('-f', '--force', action="store_true",
            help='force overwrite exist SRT files')
    parser.add_argument('files', nargs='*',
            help='paths of ASS/SSA files (default: all on current directory)')
    return parser.parse_args()


def _check_chardet():
    """Import chardet or exit."""
    global chardet
    try:
        import chardet
    except ImportError:
        print('Error: module "chardet" not found.\nPlease install it ' + \
                '(pip install chardet) or specify a encoding (-e utf-8).',
                file=sys.stderr)
        sys.exit(1)


def _check_langconv():
    """Import langconv or exit."""
    global langconv
    try:
        import langconv
    except ImportError:
        print('Error: module "langconv" not found.\n' + \
                'Please download it or disable translation.')
        sys.exit(1)


def _detect_charset(file):
    """Try detect the charset of file, return the name of charset or exit."""
    bytes = file.read(4096)
    file.seek(0)
    c = chardet.detect(bytes)
    if c['confidence'] < 0.3:
        print('Error: unknown file encoding, ' + \
                'please specify one by -e.', file=sys.stderr)
        sys.exit(1)
    elif c['confidence'] < 0.6:
        print('Warning: uncertain file encoding, ' + \
                'suggest specify one by -e.', file=sys.stderr)
    return c['encoding']


def _files_on_cwd():
    """Return all ASS/SSA file on current working directory. """
    files = []
    for file in os.listdir(os.getcwd()):
        if file.startswith('.'):
            continue
        if file.endswith('.ass'):
            files.append(file)
        elif file.endswith('.ssa'):
            files.append(file)
    return files


def _combine_output_file_path(in_files, output_dir):
    files = []
    for file in in_files:
        name = os.path.splitext(os.path.basename(file))[0] + '.srt'
        path = os.path.join(output_dir, name)
        files.append((file, path))
    return files


def _convert_files(files, args):
    if args.encoding:
        in_codec = codecs.lookup(args.encoding)
    else:
        in_codec = None
    if args.srt_encoding:
        out_codec = codecs.lookup(args.srt_encoding)
    else:
        out_codec = in_codec

    sum = len(files)
    done = 0
    fail = 0
    ignore = 0
    print("Found {} file(s), converting...".format(sum))
    for in_path, out_path in _combine_output_file_path(files, args.output_dir):
        print("\t({:02d}/{:02d}) is converting... " \
                .format(done + fail + ignore + 1, sum), end='')
        if not args.force and os.path.exists(out_path):
            print('[ignore] (SRT exists)')
            ignore += 1
            continue
        try:
            with open(in_path, 'rb') as in_file:
                if args.encoding is None:  # Detect file charset.
                    in_codec = codecs.lookup(_detect_charset(in_file))
                    if args.srt_encoding is None:
                        out_codec = in_codec

                out_str = asstosrt.convert(in_codec.streamreader(in_file),
                        args.language, args.no_effact, args.only_first_line)

            with open(out_path, 'wb') as out_file:
                out_file.write(out_codec.encode(out_str)[0])
            done += 1
            print('[done]')

        except (UnicodeDecodeError, UnicodeEncodeError, LookupError) as e:
            print('[fail] (codec error)')
            print(e, file=sys.stderr)
        except ValueError as e:
            print('[fail] (irregular format)')
            print(e, file=sys.stderr)
        except IOError as e:
            print('[fail] (IO error)')
            print(e, file=sys.stderr)

    print("All done:\n\t{} success, {} ignore, {} fail." \
            .format(done, ignore, sum - done - ignore))


def main():
    args = _get_args()
    if args.encoding is None:  # Enable auto detect
        _check_chardet()

    if args.language is not None:
        _check_langconv()
    
    files = args.files
    if not files:
        files = _files_on_cwd()
    if not files:
        print('ASS/SSA file no found.\nTry --help for more information',
                file=sys.stderr)
        sys.exit(1)

    _convert_files(files, args)
