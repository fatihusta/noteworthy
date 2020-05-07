#!/usr/bin/env python
import os
import sys
import time
from pathlib import Path
from procz import ProcManager, TimedLoop

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(CURR_PATH, 'tmptest')

class RunWhileFileProc:
    def __init__(self, file_path):
        self.file_path = file_path

    def run(self):
        while self._file_exists():
            time.sleep(1)

    def _file_exists(self):
        return os.path.isfile(self.file_path)

def _get_manager():
    return ProcManager(lock_dir=TEST_DIR)

def setup():
    Path(TEST_DIR).mkdir(exist_ok=True, parents=True)

def tear_down():
    m = _get_manager()
    os.system(f'rm -rf {TEST_DIR}')
    with TimedLoop(2) as l:
        procs = l.run_til(lambda: os.path.exists(TEST_DIR), lambda x: not x)

def start_proc():
    m = _get_manager()
    expected_pid_file = 'procz_test.pid'
    expected_pid_path = os.path.join(TEST_DIR, expected_pid_file)
    m.start_proc('test', lambda: RunWhileFileProc(expected_pid_path))

def start_proc_kill_old():
    m = _get_manager()
    expected_pid_file = 'procz_test.pid'
    expected_pid_path = os.path.join(TEST_DIR, expected_pid_file)
    m.start_proc('test', lambda: RunWhileFileProc(expected_pid_path), kill_old=True)

def create_imporperly_cleaned_pidfile():
    pid_file = 'procz_test.pid'
    pid_path = os.path.join(TEST_DIR, pid_file)
    os.system(f'touch {pid_path}')

def kill_proc():
    m = _get_manager()
    m.kill_proc('test')

def assert_proc_exists():
    m = _get_manager()
    with TimedLoop(5) as l:
        procs = l.run_til(m.list_procs)
    assert 'test' == procs[0].get('name')

def assert_proc_not_exists():
    m = _get_manager()
    procs = m.list_procs()
    with TimedLoop(5) as l:
        l.run_til(m.list_procs, lambda x: not x)

MANAGER = ProcManager(lock_dir='')


FUNC_DICT = {
 'setup': setup,
 'tear_down': tear_down,
 'start_proc': start_proc,
 'start_proc_kill_old': start_proc_kill_old,
 'kill_proc': kill_proc,
 'assert_proc_exists': assert_proc_exists,
 'assert_proc_not_exists': assert_proc_not_exists,
 'create_imporperly_cleaned_pidfile': create_imporperly_cleaned_pidfile
}

if __name__ == "__main__":
    func_name = sys.argv[1]
    FUNC_DICT.get(func_name)()
