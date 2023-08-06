import sys
import os
from os.path import join as pjoin
import json
import shutil
from os import makedirs
from textwrap import dedent
from nose.tools import eq_, ok_
from .utils import (temp_working_dir,
                    temp_working_dir_fixture,
                    assert_raises,  
                    cat)
from ..fileutils import touch
from .. import build_tools
from nose import SkipTest

