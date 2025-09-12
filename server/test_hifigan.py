import sys
import os
from inspect import signature

# add project root (two levels up from server/)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)

from test_sadtalker import SadTalker  # now it should find it

print(signature(SadTalker.__init__))











