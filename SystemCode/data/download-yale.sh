#!/usr/bin/env bash
# Fetch the Yale ED visits dataset (~99 MB) from the study authors' GitHub repo.
set -euo pipefail
cd "$(dirname "$0")"
if [ -s yale_ed_visits.rdata ]; then echo "have yale_ed_visits.rdata"; exit 0; fi
curl -fSL --retry 3 -o yale_ed_visits.rdata.part \
  "https://github.com/yaleemmlc/admissionprediction/raw/master/Results/5v_cleandf.RData"
mv yale_ed_visits.rdata.part yale_ed_visits.rdata
echo "done -> data/yale_ed_visits.rdata"
