import os
import time
import pytest
from pathlib import Path
from procz import ProcManager

CURR_PATH = os.path.dirname(os.path.realpath(__file__))
HELPER_PATH = os.path.join(CURR_PATH, 'manager_test_helper.py')

class TestProcManager:

    def _call_helper(self, func_name, expect_fail=False):
        has_error = not not os.system(f'{HELPER_PATH} {func_name}')
        assert has_error == expect_fail
        if func_name.startswith('start') or func_name.startswith('kill'):
            time.sleep(2)

    def setup_method(self):
        self._call_helper('setup')

    def teardown_method(self):
        self._call_helper('tear_down')


    def test_start_proc(self):
        self._call_helper('start_proc')
        self._call_helper('assert_proc_exists')

    def test_kill_proc(self):
        self._call_helper('start_proc')
        self._call_helper('kill_proc')
        self._call_helper('assert_proc_not_exists')

    def test_manager_crashes_if_proc_already_exists(self):
        self._call_helper('start_proc')
        self._call_helper('start_proc', expect_fail=True)

    def test_manager_can_kill_old_proc(self):
        self._call_helper('start_proc')
        self._call_helper('start_proc_kill_old')
        self._call_helper('assert_proc_exists')
