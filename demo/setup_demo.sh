#!/bin/bash
poetry shell
python demo/reset_db.py
python demo/setup_admin_account.py
python demo/reset_test_account.py
python demo/generate_pastes.py
django-admin loaddata pastemate/pastes/fixtures/pastes.json