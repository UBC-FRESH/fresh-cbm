# P7 close-out: trusted publishing

Phase identifier: P7
Status: complete
Parent issue: #36
Tasks: #37 (TestPyPI), #38 (PyPI)
Workflow: `.github/workflows/release.yaml`

## Result

Published `fresh-cbm==0.2.0` with GitHub OIDC trusted publishing:

- TestPyPI: https://test.pypi.org/project/fresh-cbm/0.2.0/
- PyPI: https://pypi.org/project/fresh-cbm/0.2.0/

No PyPI token is stored in the repository.

## Evidence

- TestPyPI workflow: run 41274843015
- PyPI workflow: run 41274946753
- clean venv installs from both registries
- `fresh-cbm-verify --help` works from both installs
- package metadata: fresh-cbm 0.2.0, Python >=3.11
- dashboard and docs remain green
