#!/bin/bash

export TUNES_SHEET_ID='{{sheet_id}}'
export GOOGLE_AUTH_JSON='{{google_auth_json}}'
{{venv_dir}}/bin/python {{playbook_dir}}/tunes.py
