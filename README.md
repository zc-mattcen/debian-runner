# Debian runner container image for GitHub Actions

This is a Debian container image which can be used to run GitHub Actions that
require additional dependencies installed beyond GitHub's default Ubuntu
runner. It can be used as follows. Note the `container` declaration below.

`.github/workflows/ci.yml`:

```yaml
# yaml-language-server: $schema=https://www.schemastore.org/github-workflow.json

---

jobs:
    linttest:
        container:
            image: ghcr.io/zc-mattcen/debian-runner:latest
        name: make lint test
        runs-on: ubuntu-22.04
        steps:
            - uses: actions/checkout@v4
            - run: |
                git config --global --add safe.directory ${{ github.workspace }}
            - name: Install Dependencies
              run: |
                make build-deps

            - name: Run tests and linters
              run: |
                make -k lint test

name: CI

# yamllint disable-line rule:truthy
on:
    pull_request:
    push:
```
