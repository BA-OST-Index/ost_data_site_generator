from _main import *

ALL_LANGS = ["en", "zh_cn"]
LANG_OTHER_PAGE = {
    "page/{lang}/main_all.html": "main/index.html",
    "page/{lang}/_index.html": "index.html",
    "page/{lang}/_about.html": "about.html"
}
OTHER_STATIC_PAGE = {
    "page/index.html": "index.html",
    "page/404.html": "404.html",
    "page/zh_cn/_zhcn_technical.html": "zh_cn/zhcn_technical.html"
}

delete_old_page()
copy_static_file(True)

env = get_jinja_env()
generate_page_per_lang(ALL_LANGS, env, ["exported_data"])
generate_other_per_lang(ALL_LANGS, env, LANG_OTHER_PAGE)
generate_static_page(env, OTHER_STATIC_PAGE)