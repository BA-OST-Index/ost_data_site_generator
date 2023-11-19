from _main import *
from _main_config import *

ALL_FOLDERS = ["character"]

delete_old_page()
# copy_static_file(True)

env = get_jinja_env()
for i in ALL_FOLDERS:
    generate_page_per_lang(ALL_LANGS, env, ["exported_data", i])
generate_other_per_lang(ALL_LANGS, env, LANG_OTHER_PAGE)
generate_static_page(env, OTHER_STATIC_PAGE)

start_server(9000)
