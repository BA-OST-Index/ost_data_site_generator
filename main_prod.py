from _main import *
from _main_config import *

delete_old_page()
copy_static_file(True)

env = get_jinja_env()
generate_page_per_lang(ALL_LANGS, env, ["exported_data"])
generate_other_per_lang(ALL_LANGS, env, LANG_OTHER_PAGE)
generate_static_page(env, OTHER_STATIC_PAGE)
