#!/bin/bash
rm -r media/embed
django-admin reset_db
django-admin setup_admin
django-admin reset_test_user
django-admin generate_demo_pastes
django-admin loaddata pastemate/pastes/fixtures/pastes.json
django-admin regenerate_embed_images
cp pastemate/demo/demo_base_template.html templates/_base.html