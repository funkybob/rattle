#!/bin/bash

set -e
set -x

case "${TOX_ENV}" in
    pypy)
        mkdir -p `pwd`/../pypy/
        wget https://bitbucket.org/pypy/pypy/get/default.tar.bz2 -O `pwd`/../pypy/pypy.tar.bz2
        tar -xf `pwd`/../pypy/pypy.tar.bz2 -C `pwd`/../pypy/
        export PYPY_LOCATION=`python -c "import glob; import os; print os.path.abspath(glob.glob('../pypy/pypy-pypy*')[0])"`
        ;;
    pypy3)
        mkdir -p `pwd`/../pypy3/
        wget https://bitbucket.org/pypy/pypy/get/py3k.tar.bz2 -O `pwd`/../pypy3/pypy.tar.bz2
        tar -xf `pwd`/../pypy3/pypy.tar.bz2 -C `pwd`/../pypy3/
        export PYPY_LOCATION=`python -c "import glob; import os; print os.path.abspath(glob.glob('../pypy3/pypy-pypy*')[0])"`
        ;;
    *)
        export PYPY_LOCATION=""
        ;;
esac

tox -e ${TOX_ENV}
