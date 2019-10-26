import pathlib
import os
import stat
from io import BytesIO
from shutil import copyfile
import sys
import warnings

from fastai.vision import load_learner, open_image

MODEL_PATH = os.getenv('MODEL_PATH') or '.'
learner = load_learner(MODEL_PATH)
DOC_LABEL = 'docs'
DOC_THRESHOLD = 0.5
warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.functional")  # noqa


def check_if_doc(path):
    with open(path, 'rb') as fp:
        img = BytesIO(fp.read())
        try:
            img = open_image(img)
        except OSError:
            return False
        _, _, losses = learner.predict(img)
        predictions = dict(zip(learner.data.classes, map(float, losses)))
        if predictions[DOC_LABEL] > DOC_THRESHOLD:
            return True
        return False


def filter_dir(path, outdir, root_src):
    root = pathlib.Path(path)
    for item in os.listdir(root):
        path = root.joinpath(item)
        if os.path.isfile(path):
            if check_if_doc(path):
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


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Need 2 arguments: the source directory and the destination")
    source = pathlib.Path(sys.argv[1])
    assert source.exists()
    dest = pathlib.Path(sys.argv[2])
    assert dest.exists()
    filter_dir(source, dest, source)
