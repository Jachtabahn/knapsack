import sys
import subprocess
from os import path
import json
import time
import argparse
import logging

def measure_runtime(command_list, input_filepath, output_filepath, index, amount, often):
    runtimes = []
    for _ in range(often):
        input_file = open(input_filepath)
        output_file = open(output_filepath, 'w') if output_filepath is not None else None
        logging.info('\n\n')
        logging.info(f'----------- #{index}/{amount} INPUT {input_filepath} -----------')
        start = time.time()
        try:
            subprocess.run(command_list,
                stdin=input_file,
                stdout=output_file,
                check=True,
                stderr=sys.stderr)
        except Exception as e:
            logging.error(f'Solver process executed abnormally! Skipping {input_filepath}.')
            logging.error(e)
            return None
        runtime = time.time() - start
        runtimes.append(runtime)
        logging.info(f'***************** Ran in {runtime}s *****************')
        input_file.close()
        if output_file is not None:
            output_file.close()
    return runtimes

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', '-c', required=True)
    parser.add_argument('--often', '-o', type=int, default=1)
    parser.add_argument('--extension', '-e', type=str, default='')
    parser.add_argument('--verbose', '-v', action='count')
    parser.add_argument('input_paths', type=str, nargs='+')
    args = parser.parse_args()

    log_levels = {
        None: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }
    if args.verbose is not None and args.verbose >= len(log_levels):
        args.verbose = len(log_levels)-1
    logging.basicConfig(format='%(message)s', level=log_levels[args.verbose])

    try:
        with open('info.json') as f: info = json.load(f)
    except:
        info = {}

    for index, filepath in enumerate(args.input_paths):
        if args.extension:
            output_filepath = filepath + args.extension
        else:
            output_filepath = None

        runtimes = measure_runtime(
            args.command.split(),
            filepath,
            output_filepath,
            index+1,
            len(args.input_paths),
            args.often)

        _, basename = path.split(filepath)
        dot_index = basename.rfind('.')
        basename = basename[:dot_index]
        if basename not in info:
            info[basename] = {}
        if 'runtimes' not in info[basename]:
            info[basename]['runtimes'] = []
        info[basename]['runtimes'].extend(runtimes)

    with open('info.json', 'w') as f:
        f.write(json.dumps(info, indent=4))
