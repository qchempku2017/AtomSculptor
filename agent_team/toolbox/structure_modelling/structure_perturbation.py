#!/usr/bin/env python3
import os
import sys

os.environ.setdefault('ATOMSCULPTOR_SANDBOX_ROOT', '/home/notfish/dev/AtomSculptor/sandbox/.runtime')
PYTHON_EXECUTABLE = '/home/notfish/dev/AtomSculptor/.venv/bin/python'
IMPL_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'structure_perturbation_impl.py')
os.execv(PYTHON_EXECUTABLE, [PYTHON_EXECUTABLE, IMPL_SCRIPT, *sys.argv[1:]])
