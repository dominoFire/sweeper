#! /bin/bash

#Script for cleaning cloud resources used by PerfKitBenchmarker
set -e
set -v

# Virtual Machines
azure vm list --json | jq '. [] | .VMName' | grep perfkit | xargs -t -I{} azure vm delete --blob-delete --quiet --verbose {}

# Virtual networks
azure network vnet list --json | jq '. [] | .name' | grep perfkit | xargs -t -I{} azure network vnet delete --quiet --verbose {}

# Storage accounts
azure storage account list --json | jq '. [] | .name' | grep perfkit | xargs -t -I{} azure storage account delete --verbose --quiet {}

# Cloud services
azure service list --json | jq '. [] | .serviceName' | grep perfkit | xargs -t -I{} azure service delete --verbose --quiet {} 
