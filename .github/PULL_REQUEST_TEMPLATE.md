# HACS Default Repository Submission (Template)

> Use this template when opening a PR to **HACS default** (https://github.com/hacs/default).  
> If you are opening a PR in *this* repo, adjust wording accordingly.

## Summary
- **Integration name:** Solar of Things
- **Repository:** https://github.com/conexocasa/solar-of-things-ha
- **Category:** Integration
- **Domain:** `solar_of_things`
- **Maintainer:** @conexocasa

## What this PR adds/changes
- Adds the **Solar of Things (Siseli)** Home Assistant custom integration to the HACS default repository.

## Validation checklist
- [ ] The repository contains `custom_components/solar_of_things/manifest.json`
- [ ] `manifest.json` has a valid `version`
- [ ] `hacs.json` exists in the repository root
- [ ] Installation works via HACS (custom repository install test)
- [ ] The integration can connect using `IOT-Token` from https://solar.siseli.com [Source](https://solar.siseli.com)
- [ ] Auto-discovers devices by Station ID (calls `/apis/device/list`)

## User-facing documentation
- README: https://github.com/conexocasa/solar-of-things-ha#readme
- Troubleshooting: https://github.com/conexocasa/solar-of-things-ha/blob/main/TROUBLESHOOTING.md

## Notes
- API behavior is based on the Siseli portal and the reference client: https://github.com/Hyllesen/solar-of-things-solar-usage [Source](https://github.com/Hyllesen/solar-of-things-solar-usage)

