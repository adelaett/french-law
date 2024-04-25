from subprocess import run, PIPE
from pathlib import Path
import os
from itertools import product
import shutil

import base64
import os
import hashlib  # for stable hash accross runs

env_base = dict(os.environ)


for optim, avoid_exceptions in product(["yes", "no"], repeat=2):

    other = {"NODOC": "yes",
             "CATALA_FLAGS": "",
             "CATALA_TRACE": "no",
             "CATALA_OPTIMIZE": optim,
             "CATALA_AVOID_EXCEPTIONS": avoid_exceptions}

    tmp_dir = (Path(
        '.')/'ex'/hashlib.md5(repr(tuple(sorted(other.items()))).encode('utf-8')).hexdigest()).absolute()

    print(
        f"optim: {optim}, avoid_exceptions: {avoid_exceptions}, directory: {tmp_dir}"
    )

    if not (tmp_dir.exists() and tmp_dir.is_dir()):

        run(["make", "clean", "local-install"],
            cwd="../catala-examples",
            capture_output=True,
            check=True, env=env_base | {"INSTALL_PREFIX": tmp_dir} | other
            )

    # Bien garder les deux lignes.

    # interprete catala.
    # run(["make", "dependencies_python"], check=True,
    #     env=env_base | {"OCAMLPATH": tmp_dir/"lib"})
    # run(["make", "bench_python"], check=True,
    #     env=env_base | {"OCAMLPATH": tmp_dir/"lib"})

    # Plutot le throughput.

    # C'est quoi l'argument pour le python ? -> on regarde tous les languages.
    # c'est mieux dans tous les cas donc c'était une bonne chose.

    run(["make", "bench_ocaml"], check=True,
        stderr=PIPE,
        env=env_base | {"OCAMLPATH": tmp_dir/"lib"})

    print()

    # shutil.rmtree(tmp_dir)
