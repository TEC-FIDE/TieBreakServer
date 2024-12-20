# TieBreakServer

| **Category** | **Status' and Links**                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------- |
| General      | [![][maintenance_y_img]][maintenance_y_lnk] [![][semver_pic]][semver_link]                                                |
| CI           | [![][pre_commit_ci_img]][pre_commit_ci_lnk] [![][codecov_img]][codecov_lnk] [![][gha_docu_img]][gha_docu_lnk]             |
| Github       | [![][gh_issues_img]][gh_issues_lnk] [![][gh_language_img]][gh_language_lnk] [![][gh_last_commit_img]][gh_last_commit_lnk] |

The **TieBreakServer** is an open-source project initiated by the FIDE Technical Committee.
Its purpose is to provide a
service for developers of pairing systems, with the following goals:

- **Fast and Accurate Tie-Break Calculations**: Enable pairing programs to compute tie-breaks efficiently and
  accurately.
- **Rapid Implementation of Latest Rules & Regulations**: Accelerate the process of implementing the most recent
  regulations, reducing the turnaround time between the publication of updated rules and their integration into
  pairing programs.
- **Uniform and Consistent Tie-Break Calculations**: Ensure uniformity and consistency in tie-break calculations
  across different systems.

## Acknowledgements

The source code for the Tiebreak Server was generously donated by Otto Milvang.
We are deeply grateful for his
contribution, which has made this open-source project possible.

## Usage

Here’s a refined version of your message:The code can be used in three different ways:

1. By accessing the **API server**.
1. By copying[^1] the code to your local server/installation and running it locally.
1. By copying[^1] specific code snippets and integrating them into your own codebase.

### API Server

-

### Local Installation

1. Install python 3, minimum version 3.10.

1. Clone the repository to your target machine.

1. In the directory where the tiebreakchecker.py exists:

```bash
python  tiebreakchecker.py
```

> **Command line parameters:**
>
> **-i** or **--input-file** - Tournament file<br>
> **-o** or **--output-file** - Output file, use *-* for stdout<br>
> **-f** or **--file-format** - TRF for <A HREF="https://www.fide.com/FIDE/handbook/C04Annex2_TRF16.pdf">FIDE
> TRF-16</A>, JCH for Chess-JSON, TS for Tournament Service files<br>
> **-e** or **--event-number** - In files with multiple event, tournaments are numbered 1,2,3, ... use 0 for
> passthrough<br>
> **-n** or **--number-of-rounds** - Number of rounds in Tie-break calculation><br>
> **-d** or **--delimiter** - Predefined delimiters B=blank, T=tab, S=Semicolon, C=comma, default is JSON output<br>
> **-t** or **--tie-break** - List of Rank order specifiers

> Rank order specifiers
>
> The Rank order specifiers has the form **TB:PS#Mn-optlist**
>
> - **TB** - required, TieBreak name
> - **:PS** - Point system name for team competitions, <br>MP=match points(default), <br>GP=game points
> - **#Mn** - Modifier<br>C=cut, <br>M=medial, <br>L=limit, <br>n=number
> - **-optlist** -<br>
>   \- P - forfeited games, either wins or losses, are considered as played games against the scheduled opponent <br>
>   \- U - all unplayed rounds are considered as Draws - against themselves (DAT) to compute the participant's TB<br>
>   \- V - the article 14.6 is ignored, i.e., the least significant value is cut, regardless of the surroundings<br>

> **Examples**
>
> - **PTS** - Points<br>
> - **BH:GP#C1** - Buchholz cut-1 calculated on game points
> - **DE-P** - Direct encounter, forfeited games, either wins or losses, are considered as played games against the
>   scheduled opponent <br>

## Contributing

### Requirements

1. PEP 8
1. Linting and formatting
1. TTD
1. CI/CD

### Recommendations

1. Use virtual environment.
1. Install VEnvIt to facilitate.

## Optional links

- [Original TiebreakServer Source Code by Otto Milvang](https://github.com/OttoMilvang/TieBreakServer)
- [Original TiebreakServer Webpage](https://fide-tec.gacrux.no:9001/tbs/tbs.html)
- [C.07 FIDE Tie-Break Regulations](https://handbook.fide.com/chapter/TieBreakRegulations082024)
- [Mandatory Tie-Breaks](https://tec.fide.com/2024/04/30/mandatory-tie-breaks/)
- [FIDE Technical Commission](https://tec.fide.com/)

\[^1\]: [Refer to the license agreement](https://github.com/TEC-FIDE/TieBreakServer/blob/master/LICENSE)

[codecov_img]: https://img.shields.io/codecov/c/gh/FIDE-TEC/tiebreakserver "CodeCov"
[codecov_lnk]: (https://app.codecov.io/gh/FIDE-TEC/tiebreakserver) "CodeCov"
[gha_docu_img]: https://img.shields.io/readthedocs/FIDE-TEC "Read the Docs"
[gha_docu_lnk]: https://github.com/FIDE-TEC/tiebreakserver/blob/master/.github/workflows/02-check-documentation.yml "Read the Docs"
[gh_issues_img]: https://img.shields.io/github/issues-raw/FIDE-TEC/tiebreakserver "GitHub - Issue Counter"
[gh_issues_lnk]: https://github.com/FIDE-TEC/tiebreakserver/issues "GitHub - Issue Counter"
[gh_language_img]: https://img.shields.io/github/languages/top/FIDE-TEC/tiebreakserver "GitHub - Top Language"
[gh_language_lnk]: https://github.com/FIDE-TEC/tiebreakserver "GitHub - Top Language"
[gh_last_commit_img]: https://img.shields.io/github/last-commit/FIDE-TEC/tiebreakserver/master "GitHub - Last Commit"
[gh_last_commit_lnk]: https://github.com/FIDE-TEC/tiebreakserver/commit/master "GitHub - Last Commit"
[maintenance_y_img]: https://img.shields.io/badge/Maintenance%20Intended-%E2%9C%94-green.svg?style=flat-square "Maintenance - intended"
[maintenance_y_lnk]: http://unmaintained.tech/ "Maintenance - intended"
[pre_commit_ci_img]: https://img.shields.io/github/actions/workflow/status/FIDE-TEC/tiebreakserver/01-pre-commit-and-document-check.yml?label=pre-commit "Pre-Commit"
[pre_commit_ci_lnk]: https://github.com/FIDE-TEC/tiebreakserver/blob/master/.github/workflows/01-pre-commit-and-document-check.yml "Pre-Commit"
[semver_link]: https://semver.org/ "Sentic Versioning - 2.0.0"
[semver_pic]: https://img.shields.io/badge/Semantic%20Versioning-2.0.0-brightgreen.svg?style=flat-square "Sentic Versioning - 2.0.0"
