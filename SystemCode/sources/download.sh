#!/usr/bin/env bash
# Fetch the source documents that cannot be committed (copyright), plus re-fetch
# the public-domain ones if missing. Idempotent: skips files that already exist.
set -euo pipefail
cd "$(dirname "$0")"
UA="Mozilla/5.0"

get () {  # get <filename> <url> [fallback-url]
  if [ -s "$1" ]; then echo "have    $1"; return; fi
  echo "fetching $1"
  curl -fSL -A "$UA" --retry 3 -o "$1.part" "$2" || { [ $# -ge 3 ] && curl -fSL -A "$UA" --retry 3 -o "$1.part" "$3"; }
  mv "$1.part" "$1"
}

# ESI v5 handbook (© ENA) — public copy hosted by the California ENA chapter
get ESI-Handbook-5th-Edition-3-2023.pdf \
    "https://californiaena.org/wp-content/uploads/2023/05/ESI-Handbook-5th-Edition-3-2023.pdf"

# ESI v4 handbook (AHRQ, public domain; committed, but re-fetchable) — govinfo, mirror fallback
get ESI-Handbook-v4-2012-AHRQ.pdf \
    "https://www.govinfo.gov/content/pkg/GOVPUB-HE20_6500-PURL-gpo23161/pdf/GOVPUB-HE20_6500-PURL-gpo23161.pdf" \
    "https://sgnor.ch/fileadmin/user_upload/Dokumente/Downloads/Esi_Handbook.pdf"

# CDC Field Triage 2011 (public domain; committed, but re-fetchable) — cdc.gov original is dead, Internet Archive copy
get CDC-Field-Triage-2011-MMWR.pdf \
    "https://web.archive.org/web/2020id_/https://www.cdc.gov/mmwr/pdf/rr/rr6101.pdf"

# NICE NG232 main guideline (© NICE) — NCBI Bookshelf mirror (nice.org.uk blocks CLI clients)
get NICE-NG232-main-guideline.pdf \
    "https://www.ncbi.nlm.nih.gov/books/NBK592586/pdf/Bookshelf_NBK592586.pdf"

echo
echo "Done. NICE evidence reviews I/J (optional background) must be downloaded manually"
echo "in a browser: https://www.nice.org.uk/guidance/ng232/evidence"
