from subprocess import run
from pathlib import Path
import os
from itertools import product
import tempfile
import shutil

env_base = dict(os.environ)


for optim, avoid_exceptions in product(["yes", "no"], repeat=2):
    tmp_dir = Path(tempfile.mkdtemp())
    print(
        f"optim: {optim}, avoid_exceptions: {avoid_exceptions}, directory: {tmp_dir}"
    )
    run(["make", "clean", "local-install"],
        cwd="../catala-examples",
        capture_output=True,
        check=True, env=env_base | {"INSTALL_PREFIX": tmp_dir,
                                    "NODOC": "yes",
                                    "CATALA_FLAGS": "",
                                    "CATALA_TRACE": "no",
                                    "CATALA_OPTIMIZE": optim,
                                    "CATALA_AVOID_EXCEPTIONS": avoid_exceptions}
        )
    run(["make", "bench_ocaml"], check=True,
        env=env_base | {"OCAMLPATH": tmp_dir/"lib"})

    print()

    shutil.rmtree(tmp_dir)
