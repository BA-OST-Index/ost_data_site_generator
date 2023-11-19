import time

ALL_LANGS = ["en", "zh_cn"]


def render_template(env, path):
    print(f"[INFO]\tTesting {path}...")
    try:
        template = env.get_template(path)

        start = time.time_ns()
        template.render(is_static=True)
        end = time.time_ns()
    except Exception as e:
        print(f"[FAIL]\tFailed with exception: {str(e)}")
        raise e
    else:
        print(f"[OK]\tSuccessfully tested (runtime {(end - start) / 1e6} ms)")


def check_static_per_lang(env, page: dict):
    total = len(page.keys())
    failed_count = 0

    for i in ALL_LANGS:
        for path, name in page.items():
            try:
                render_template(env, path.format(lang=i))
            except Exception:
                failed_count += 1

    print(f"Total {total}, failed {failed_count} ({failed_count / total * 100:0.2f}%)")
    if failed_count != 0:
        raise AssertionError


def check_static_otehr(env, page: dict):
    total = len(page.keys())
    failed_count = 0

    for path, name in page.items():
        try:
            render_template(env, path.format(lang=i))
        except Exception:
            failed_count += 1

    print(f"Total {total}, failed {failed_count} ({failed_count / total * 100:0.2f}%)")
    if failed_count != 0:
        raise AssertionError
