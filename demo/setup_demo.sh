#!/bin/bash
poetry shell
python demo/reset_db.py
python setup_admin_account.py
django-admin loaddata pastemate/accounts/fixtures/users.json
python generate_pastes.py
django-admin loaddata pastemate/pastes/fixtures/pastes.json