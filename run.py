import subprocess
import time
import argparse
import logging

def measure_runtime(command_dir, command_list, input_filepath, index, amount, often):
    runtimes = []
    for _ in range(often):
        input_file = open(input_filepath)
        logging.info('\n\n')
        logging.info(f'----------- #{index}/{amount} INPUT {input_filepath} -----------\n')
        start = time.time()
        try:
            process = subprocess.run(command_list,
                stdin=input_file,
                cwd=command_dir,
                check=True,
                stderr=subprocess.PIPE)
        except Exception as e:
            logging.error(f'Solver process executed abnormally! Skipping {input_filepath}.')
            logging.error(e)
            return None
        runtime = time.time() - start
        runtimes.append(runtime)
        logging.info(process.stderr.decode())
        logging.info(f'***************** Ran in {runtime}s *****************')
        input_file.close()
    return runtimes

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', '-c', required=True)
    parser.add_argument('--often', '-o', type=int, default=1)
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

    for index, filepath in enumerate(args.input_paths):
        runtimes = measure_runtime('.', args.command.split(), filepath, index+1, len(args.input_paths), args.often)
