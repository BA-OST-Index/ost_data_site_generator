from _main import get_jinja_env, GeneratorTool
from _main_config import *
from precheck_script.check_template import check_template
from precheck_script.check_static import check_static_per_lang, check_static_otehr

env = get_jinja_env()
encounter_exception = False

try:
    check_template(env, GeneratorTool.return_template)
except AssertionError:
    encounter_exception = True

try:
    check_static_per_lang(env, LANG_OTHER_PAGE)
except AssertionError:
    encounter_exception = True

try:
    check_static_otehr(env, OTHER_STATIC_PAGE)
except AssertionError:
    encounter_exception = True

if encounter_exception:
    raise AssertionError
