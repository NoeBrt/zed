# Collapsible repository sections — real Zed captures

These screenshots were captured from a macOS development build of Zed at code commit `26a138e57f31d41b5e88fd8b297041f6da48dd73`.

The GIF is a sequence of actual screenshots captured while expanding repository sections and opening the pipeline history. It is a step-through demonstration, not continuous video. No UI or image was generated. Screenshots are converted to PNG; GIF frames are resized to 1200×780.

All repositories, authors, commits, and source files shown are fictional. The project has a SaaS backend, a SaaS frontend, and a data pipeline. Language servers are disabled for these illustrative files.

## Reproduce the project

Requires Python 3 and Git. In a disposable directory:

```sh
python3 create_demo.py northstar-demo
```

The script creates three repositories with three commits each, local bare remotes, and nine staged/unstaged changes. It refuses to overwrite an existing project. Open `northstar-demo` in the PR build of Zed, open the Git panel, select staging groups, and expand the repository sections. The included project setting `file_scan_depth: 0` activates all three nested repositories. No server or external Git remote is used.

For the displayed drafts, enter `Add cursor pagination to invoices` in backend and `Add billing dashboard pagination` in frontend. Use One Dark or One Light, a 390 px Git panel, and a 14 px UI font.
