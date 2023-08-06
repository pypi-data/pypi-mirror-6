from pprint import pprint
from os.path import join as pjoin
from textwrap import dedent
from ...core.test.utils import (temp_working_dir,
                                temp_working_dir_fixture,
                                assert_raises,  
                                cat)
from .. import package
from .. import hook_api
from ...formats.marked_yaml import marked_yaml_load, yaml_dump
from ..exceptions import ProfileError
from nose import SkipTest