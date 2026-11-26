#!/usr/bin/env python3
"""Reconstruit data/raw/advisories à partir de la GitHub Advisory Database (format OSV).

Sélection : avis "reviewed", Maven et npm, N avis par couple (écosystème, sévérité),
triés par identifiant (déterministe). Les avis sans description ou retirés sont ignorés.

Usage :
    python3 scripts/fetch_advisories.py                 # clone puis sélectionne
    python3 scripts/fetch_advisories.py --src <dossier> # dépôt déjà cloné
"""
import argparse, collections, glob, json, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "https://github.com/github/advisory-database.git"
PATHS = ["advisories/github-reviewed/2021/12", "advisories/github-reviewed/2022"]
ECOSYSTEMS = ("Maven", "npm")
ALWAYS = "GHSA-jfh8-c2jp-5v3q"  # Log4Shell (CVE-2021-44228)


def clone(dest):
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", REPO, dest], check=True)
    subprocess.run(["git", "-C", dest, "sparse-checkout", "set", *PATHS], check=True)


def select(src, per):
    buckets = collections.defaultdict(list)
    log4shell = None
    for f in sorted(glob.glob(f"{src}/advisories/github-reviewed/**/*.json", recursive=True)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if d["id"] == ALWAYS:
            log4shell = f
        sev = (d.get("database_specific") or {}).get("severity")
        if not d.get("details") or d.get("withdrawn") or not sev:
            continue
        ecos = {a.get("package", {}).get("ecosystem") for a in d.get("affected", [])}
        for e in ECOSYSTEMS:
            if e in ecos:
                buckets[(e, sev)].append((e, d["id"], f))
    chosen = [x for k in sorted(buckets) for x in buckets[k][:per]]
    if log4shell and not any(i == ALWAYS for _, i, _ in chosen):
        chosen.append(("Maven", ALWAYS, log4shell))
    return chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src")
    ap.add_argument("--dst", default=str(ROOT / "data/raw/advisories"))
    ap.add_argument("--per", type=int, default=40)
    a = ap.parse_args()

    tmp = None
    src = a.src
    if not src:
        tmp = tempfile.mkdtemp()
        clone(tmp)
        src = tmp
    chosen = select(src, a.per)
    for e, i, f in chosen:
        out = Path(a.dst) / e.lower()
        out.mkdir(parents=True, exist_ok=True)
        shutil.copy(f, out / f"{i}.json")
    print(f"{len(chosen)} avis copiés dans {a.dst}")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
