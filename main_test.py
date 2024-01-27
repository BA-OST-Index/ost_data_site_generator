from _main import *
from _main_config import *
from main_tool import INIT_TIME
from main_tool_2 import generate_tooltip, rename_js

delete_old_page()

env = get_jinja_env()
# generate_tooltip(env)
rename_js(INIT_TIME)

copy_static_file(True)

generate_page_per_lang(ALL_LANGS, env, ["exported_data"])
generate_other_per_lang(ALL_LANGS, env, LANG_OTHER_PAGE)
generate_static_page(env, OTHER_STATIC_PAGE)
