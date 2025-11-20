# al - The Alias Manager

`al` is a streamlined CLI tool for managing shell aliases on Linux and macOS systems. It simplifies the creation, organization, and synchronization of your command shortcuts, keeping your shell configuration clean and portable.

## Features

- **Grouped Aliases**: Organize aliases into groups (e.g., `git`, `docker`, `system`) for better management.
- **Interactive Management**: Easily add and remove aliases with interactive prompts.
- **Search**: Quickly find aliases by name or command content.
- **Cloud Sync**: Synchronize your aliases across machines using GitHub Gists.
- **Shell Integration**: Works seamlessly with `zsh` and `bash`.
- **Import**: Import existing aliases from your `.zshrc` or `.bash_aliases`.

## Installation

### Prerequisites

- Python 3.11 or higher
- `uv` (recommended) or `pip`

### Install with uv

```bash
# Clone the repository
git clone https://github.com/yourusername/al.git
cd al

# Install dependencies and the tool
uv sync
uv pip install -e .
```

### Install from PyPI

```bash
pip install al-alias-manager
# or
uv pip install al-alias-manager
```

## Quick Start

1.  **Initialize**: Set up the configuration and shell integration.
    ```bash
    al init
    ```
    Follow the instructions to source the alias file (e.g., `source ~/.config/al/aliases` or restart your terminal).

2.  **Add an Alias**:
    ```bash
    al add
    ```
    Follow the interactive prompts to create a new alias.

3.  **Use it**:
    ```bash
    # Run the alias directly from al (optional)
    al run my-alias

    # Or just use it in your shell (after sourcing)
    my-alias
    ```

## Usage

### Managing Aliases

- **Add**: Create a new alias interactively.
    ```bash
    al add
    ```

- **List**: View all aliases, optionally filtered by group.
    ```bash
    al list
    al list git  # Show only 'git' group
    ```

- **Search**: Find aliases matching a query.
    ```bash
    al search "log"
    ```

- **Remove**: Interactively select and remove an alias.
    ```bash
    al remove
    ```

- **Edit**: Open the raw alias file in your default editor (`$EDITOR`).
    ```bash
    al edit
    ```

### Synchronization (GitHub Gist)

Sync your aliases to a private GitHub Gist to share them between computers.

1.  **Push**: Upload your local aliases to Gist.
    ```bash
    al sync push
    ```
    *On first run, you will be asked for a GitHub Personal Access Token (with `gist` scope).*

2.  **Pull**: Download aliases from Gist.
    ```bash
    al sync pull
    ```
    *You will need the Gist ID (provided after a successful push).*

### Importing

Import existing aliases from a file (e.g., your `.zshrc`).

```bash
al import ~/.zshrc
```
This will parse `alias name='command'` lines and add them to an `imported` group.

## Development

This project uses `uv` for dependency management and `ruff` for linting/formatting.

```bash
# Run tests
uv run pytest

# Run linting
uv run ruff check .
```

## License

[GPLv3](LICENSE)
