#!/bin/bash

# https://superuser.com/a/352290
if [ -z "$(ls -A "$DIRECTORY_SCOPUS")" ]; then
    echo "Creating the my_scopus.py file with MY_API_KEY value from the"
    echo "environment variable API_KEY."
    echo "MY_API_KEY = '$API_KEY'" > "$DIRECTORY_SCOPUS"/my_scopus.py
fi

/bin/bash
