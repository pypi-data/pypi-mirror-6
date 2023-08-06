import os.path
from pkgutil import get_data


def read(name):
    return get_data('sbdk.resources', name)


def copy(name,  dst):
    joined = os.path.join(dst, os.path.basename(name))
    dst_name = joined if os.path.isdir(dst) else dst
    with open(dst_name, 'w') as out:
        out.write(read(name))


def process_template(file_name, dst=None, **bind_data):
    tpl = read(file_name)
    out = tpl.format(**bind_data)
    if dst:
        dst_name = dst
        if os.path.exists(dst) and os.path.isdir(dst):
            dst_name = os.path.join(dst, file_name)
        with open(dst_name, 'w') as of:
            of.write(out)
    return out
