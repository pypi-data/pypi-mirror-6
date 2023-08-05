#!/bin/bash

echo "Starting drest.mockapi..."
pushd utils/drest.mockapi
    pip install -r requirements.txt
    python setup.py develop --no-deps
    python mockapi/manage.py testserver fixtures/initial_data.json DREST_MOCKAPI_PROCESS
    sleep 5
popd
