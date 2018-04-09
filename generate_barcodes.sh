#!/usr/bin/env bash

python paper_generator.py MASTER testing
python paper_generator.py MASTER training
python paper_generator.py pick-by-paper_barcode training
python paper_generator.py pick-by-paper_barcode testing
python paper_generator.py pick-by-paper_none testing
python paper_generator.py pick-by-paper_none training
