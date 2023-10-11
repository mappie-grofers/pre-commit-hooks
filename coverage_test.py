import os
import subprocess
import sys

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"

# Detail of coverage will be stored in following file
COVERAGE_FILE = 'coverage.out'


def run_coverage_check(settings_file):
    settings = {}
    with open(settings_file, 'r') as file:
        exec(file.read(), settings)
        # Access variable values
    THRESHOLD = settings.get('THRESHOLD', 100)
    BUILD_DIR = settings.get('BUILD_DIR', 'build')
    EXCLUDE_DIRS = settings.get('EXCLUDE_DIRS', [])
    EXCLUDE_FILES = settings.get('EXCLUDE_FILES', [])

    PKGS = subprocess.check_output(['go', 'list', './...'], universal_newlines=True)
    PKGS_LIST = PKGS.split('\n')

    if EXCLUDE_DIRS:
        PKGS = [pkg for pkg in PKGS_LIST if not any(exclude_dir in pkg for exclude_dir in EXCLUDE_DIRS)]

    os.makedirs(BUILD_DIR, exist_ok=True)

    PKGS_LIST = list(filter(lambda item: item != '', PKGS_LIST))
    print(PKGS_LIST)
    subprocess.run(['go', 'test'] + PKGS_LIST + ['-coverprofile=', COVERAGE_FILE], check=True)

    for p in EXCLUDE_FILES:
        subprocess.run(['sed', '-i.bak', '-e', '/{0}/d'.format(p), COVERAGE_FILE])


    coverage_output = subprocess.check_output(['go', 'tool', 'cover', '-func=' + COVERAGE_FILE], universal_newlines=True)
    print(coverage_output)
    total_coverage = [line for line in coverage_output.split('\n') if 'total' in line][0].split()[2][:-1]

    print("Total coverage: {0}%. Threshold: {1}%.".format(total_coverage, THRESHOLD))

    if float(total_coverage) < THRESHOLD:
        print(RED + "Code coverage should be {0}%. Failing...".format(THRESHOLD) + RESET)
        sys.exit(1)
    else:
        print(GREEN + "Code coverage is above the threshold. Passing..." + RESET)
        sys.exit(0)

if __name__ == "__main__":
    settings_file = ".coverage_settings"
    for arg in sys.argv[1:]:
        if arg.startswith("--settings-file="):
            settings_file = arg.split("=")[1]
    run_coverage_check(settings_file)
