#! /bin/bash

set -e
set -o xtrace

export AZURE_SUBSCRIPTION_ID="8ea1a328-9162-4a6e-9cdc-fcc8d6766608"
export AZURE_PEM_FILE=./certs/azure_client.pem

python -m unittest sweeper.tests.test_workflow.PlannerTest
python -m unittest sweeper.tests.test_workflow.CreateVMTest
