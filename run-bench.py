from subprocess import run
from pathlib import Path
import os
from itertools import product

env_base = dict(os.environ)

for optim, avoid_exceptions in product(["yes", "no"], repeat=2):
    run(["opam", "reinstall", "../catala-examples/"],
        check=True, env=env_base | {"NODOC": "yes",
                                    "CATALA_FLAGS": "",
                                    "CATALA_TRACE": "no",
                                    "CATALA_OPTIMIZE": optim,
                                    "CATALA_AVOID_EXCEPTIONS": avoid_exceptions}
        )
    run(["make", "dependencies-python"],
        check=True)
    run(["make", "bench_ocaml"], check=True)
