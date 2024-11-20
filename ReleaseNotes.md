# Release 1.1.0

## General Changes

- Fixed the ISSUE_TEMPLATE's headers.
- Add CRLF in strategic places.
- Updated the install.ps1 to cater for Poetry
- Updated pyproject.toml to cater for Poetry

______________________________________________________________________

# Release 1.0.0

## General Changes

- Combined the Pre-Commit and Check-Documentation workflows to speed up processing.
- Changed RTE_ENVIRONMENT to VENV_ENVIRONMENT.
- Removed dbdef.py functionality.
- Updated .gitignore
- Renamed the install.ps1 to installpythontools.ps1 in lieu of using the pyproject.toml file to install and not
  install.ps1.
- Removed obsolete MANIFEST.in

## GitHub Issue Templates

- Replace "bold" headings with headings.
- Format according to GitHub standard.

## Pre-commit

- Set the correct parameters for formatting GitHub md-files.
- Updated hooks versions.

______________________________________________________________________

# Release 0.1.17 - 28

## General Changes

- Sample to "Send email notification"

______________________________________________________________________

# Release 0.1.3 - 16

## General Changes

- Sample to "Publish new release"

______________________________________________________________________

# Release 0.1.2

## General Changes

- Automate create a "Release" with GitHub Actions

______________________________________________________________________

# Release 0.1.1

## General Changes

- Upgrade compliance to default to MySQL 8.3.0
  - 03-ci.yml
  - docker-compose.yml
- Reorder contents of .gitignore

______________________________________________________________________

# Release 0.1.0

## General Changes

### config.py

- class Settings
- get_settings()

### dbdef.py

- db_destroy()
- user_delete()
- setup_create()
- transaction()

### Docker

- Create configuration files

### PyTest

- Create pytests

### CleanUp

- Cleanup redundant sql and ps1 files.
