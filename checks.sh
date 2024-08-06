#!/bin/sh
set -e


function heading()
{
    echo
    echo "*** $@ ***"
    echo
}


heading "Unit and integration tests"
pytest

heading "Type checks"
mypy obsessian test

heading "Style checks"
flake8 obsessian test

heading "ALL CHECKS PASS"
