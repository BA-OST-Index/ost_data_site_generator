from _main import get_jinja_env, GeneratorTool
from precheck_script.check_template import check_template

env = get_jinja_env()
check_template(env, GeneratorTool.return_template)
