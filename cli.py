import pathlib
import os
import stat
from io import BytesIO
from shutil import copyfile
import sys
import warnings
import collections

from fastai.vision import load_learner, open_image

MODEL_PATH = os.getenv('MODEL_PATH') or '.'
learner = load_learner(MODEL_PATH)
DOC_LABEL = 'docs'
DOC_THRESHOLD = 0.5
warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.functional")  # noqa


Result = collections.namedtuple("Result", "is_img, is_doc_img")


def check_if_doc_img(path):
    with open(path, 'rb') as fp:
        img = check_if_img(fp)
        if img is False:
            return Result(is_img=False, is_doc_img=False)
        _, _, losses = learner.predict(img)
        predictions = dict(zip(learner.data.classes, map(float, losses)))
        if predictions[DOC_LABEL] > DOC_THRESHOLD:
            return Result(is_img=True, is_doc_img=True)
        return Result(is_img=True, is_doc_img=False)


def check_if_img(fp):
    img = BytesIO(fp.read())
    try:
        img = open_image(img)
        return img
    except OSError:
        return False


def filter_dir(path, outdir, root_src):
    root = pathlib.Path(path)
    for item in os.listdir(root):
        path = root.joinpath(item)
        if os.path.isfile(path):
            res = check_if_doc_img(path)
            if res.is_doc_img:
                rel_path = path.relative_to(root_src)
                dest = pathlib.Path(outdir).joinpath(rel_path)
                st = os.stat(path)
                dir_path = os.path.dirname(dest)
                if not os.path.isdir(dir_path):
                    os.makedirs(dir_path)
                    os.chown(dir_path, st[stat.ST_UID], st[stat.ST_GID])
                copyfile(path, dest)
                os.chown(dest, st[stat.ST_UID], st[stat.ST_GID])
                print(f'Copied $SRC/{rel_path} to $DEST/{rel_path}')
        if os.path.isdir(path):
            filter_dir(root.joinpath(item), outdir, root_src)


def filter_inplace(path, root_src):
    root = pathlib.Path(path)
    for item in os.listdir(root):
        path = root.joinpath(item)
        if os.path.isfile(path):
            res = check_if_doc_img(path)
            if res.is_img and not res.is_doc_img:
                os.remove(path)
                rel_path = path.relative_to(root_src)
                print(f'Deleted $SRC/{rel_path}')
        if os.path.isdir(path):
            filter_inplace(root.joinpath(item), root_src)


if __name__ == '__main__':
    if len(sys.argv) not in (3, 4):
        print("""
            Usage: python cli.py filter /path/to/src /path/to/dest
            Or
            python cli.py filter_inplace /path/to/src
        """)
        sys.exit(0)
    command = sys.argv[1]
    source = pathlib.Path(sys.argv[2])
    assert source.exists()
    assert command in ('filter', 'filter_inplace')
    if command == 'filter':
        dest = pathlib.Path(sys.argv[3])
        assert dest.exists()
        filter_dir(source, dest, source)
    elif command == 'filter_inplace':
        filter_inplace(source, source)
