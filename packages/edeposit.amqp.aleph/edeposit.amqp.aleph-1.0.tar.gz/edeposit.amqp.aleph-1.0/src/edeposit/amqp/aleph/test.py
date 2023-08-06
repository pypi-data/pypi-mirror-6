#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import shelve


import convertors


#= Variables ==================================================================
FN = "tests/resources/aleph_data_examples/shelve_files/example.xml.shelve"


#= Functions & objects ========================================================



#= Main program ===============================================================
if __name__ == '__main__':
    f = shelve.open(FN)
    convertors.fromEPublication(
        f["data"]
    )
