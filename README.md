# gds-idea-pkg-tf

Terraform alias.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python package management
- [git](https://git-scm.com/)
- [gitleaks](https://github.com/gitleaks/gitleaks) for pre-commit secret scanning (`brew install gitleaks`)

## Getting started

1. Clone the repository:

   ```bash
   git clone git@github.com:co-cddo/gds-idea-pkg-tf.git
   cd gds-idea-pkg-tf
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

3. Set up pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

   This is done automatically when the project is first scaffolded.
   Pre-commit runs [ruff](https://docs.astral.sh/ruff/) on every commit
   to auto-fix lint issues and enforce formatting.

## Usage

The package installs a `tf` command (a thin wrapper around `terraform`,
defined in `src/tf/cli.py`) that groups common Terraform workflows into
short subcommands.

```bash
tf --help
```

### `tf init`

Runs `terraform init --upgrade` in the current working folder, then does
the same for every subfolder under `modules/` (if present). Before
running, it checks that `terraform` is installed (see
`src/tf/prerequisites.py`) and exits with an error if it's missing.

```bash
tf init
```

### `tf fmt`

Runs `terraform fmt --recursive` to format all `.tf` files in the
current folder and subfolders.

```bash
tf fmt
```

### `tf plan`

Runs `terraform plan -out tf.plan`, saving the plan to a `tf.plan` file
for later inspection or apply.

```bash
tf plan
```

### `tf show`

Runs `terraform show -no-color tf.plan` and writes the output to
`tfplan.txt`, producing a plain-text, colour-free version of the plan
that's easy to review or share.

```bash
tf show
```

### `tf apply`

Runs `terraform apply tf.plan`, applying the previously generated plan
file.

```bash
tf apply
```

### `tf clear`

Removes generated Terraform state artefacts: the `.terraform` folder and
`.terraform.lock.hcl` file, both in the current working folder and in
every subfolder under `modules/`.

```bash
tf clear
```

### `tf cache`

Creates a `~/.terraformrc` file (and the backing cache folder
`~/backup/terraform-cache`) configured to cache Terraform providers,
avoiding repeated downloads across projects.

```bash
tf cache
```

### `tf w`

Shows available Terraform workspaces, then selects the given workspace
(defaults to `dev`) and prints the currently selected workspace.
`dev` and `prod` are shorthands for `development` and `production`
respectively; any other value is passed through as-is.

```bash
# select/show the default "dev" (-> "development") workspace
tf w

# select the "prod" (-> "production") workspace
tf w prod

# select a custom workspace name directly
tf w staging
```

## Development

### Running tests

```bash
uv run pytest
```

### Running linting manually

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
```

### Pre-commit hooks

Pre-commit hooks run automatically on `git commit`. They will:

- **Auto-fix** lint issues detected by `ruff check --fix`
- **Auto-format** code with `ruff format`
- **Check** YAML/TOML syntax, trailing whitespace, merge conflicts
- **Scan** for leaked secrets with gitleaks
- **Prevent** direct commits to `main`

If files are modified by the hooks, the commit will be aborted.
Review the changes, `git add` them, and commit again.

To run hooks against all files manually:

```bash
uv run pre-commit run --all-files
```

## Versioning

This project uses [hatch-vcs](https://github.com/ofek/hatch-vcs) for
automatic versioning from git tags. Versions are never set manually.

On merge to `main`, the auto-release workflow creates a new tag based on
PR labels:

- `bump:major` — major version bump
- `bump:minor` — minor version bump
- (default) — patch version bump

## Licence

[MIT License](LICENCE)
