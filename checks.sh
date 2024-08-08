#!/bin/sh
set -e


function heading()
{
    echo
    echo "*** $@ ***"
    echo
}


heading "Unit and integration tests"
pytest test

heading "Type checks"
mypy markdown_run test

heading "Style checks"
flake8 markdown_run test && echo "Success: no style issue found."
