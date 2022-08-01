#!/bin/bash
rm -r media/embed
python manage.py reset_db
python manage.py setup_admin
python manage.py reset_test_user
python manage.py generate_demo_pastes
python manage.py loaddata pastemate/pastes/fixtures/pastes.json
python manage.py regenerate_embed_images
cp pastemate/demo/demo_base_template.html templates/_base.html