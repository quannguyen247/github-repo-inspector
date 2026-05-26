# GitHub Repo Inspector

A simple Python tool that uses the **GitHub REST API** to inspect a GitHub repository and generate a local report.

The tool reads repository metadata, language statistics, and the repository file tree without cloning the repository.

---

## Features

- Show repository metadata
- Show stars, forks, open issues, license, and default branch
- Count files, folders, and submodules
- Show total file size
- Show language statistics
- Show the most common file extensions
- Show the largest files
- Save the report to a local `.log` file

---

## Project Structure

```text
github-repo-inspector/
├── example/
│   └── demo.log
├── .gitignore
├── LICENSE
├── README.md
└── repo_inspector.py
```

| File | Description |
|---|---|
| `repo_inspector.py` | Main Python script |
| `example/demo.log` | Generated report |
| `.gitignore` | Git ignore rules |
| `LICENSE` | Project license |
| `README.md` | Project documentation |

---

## Requirements

Python 3 is required.

Check Python:

```bash
python3 --version
```

The tool uses only Python standard libraries.

No external package installation is required.

---

## Configuration

All settings are placed at the top of `repo_inspector.py`.

```python
REPOSITORY = "octocat/Hello-World"
OUTPUT_FILE = "example/demo.log"

TIMEOUT = 30
RETRIES = 5

TOP_EXTENSIONS = 10
TOP_FILES = 10

BASE_URL = "https://api.github.com"
TOKEN_ENV = "GITHUB_TOKEN"
```

| Setting | Description |
|---|---|
| `REPOSITORY` | Repository that the tool inspects |
| `OUTPUT_FILE` | Local report output file |
| `TIMEOUT` | Maximum wait time for one GitHub API request |
| `RETRIES` | Number of retry attempts for temporary network errors |
| `TOP_EXTENSIONS` | Number of common file extensions shown in the report |
| `TOP_FILES` | Number of largest files shown in the report |
| `BASE_URL` | GitHub API base URL |
| `TOKEN_ENV` | Environment variable name used to read the GitHub token |

The default repository is:

```python
REPOSITORY = "octocat/Hello-World"
```

To inspect another repository, edit `REPOSITORY`:

```python
REPOSITORY = "owner/repo"
```

A GitHub repository URL is also supported:

```python
REPOSITORY = "https://github.com/owner/repo"
```

To save the report to another file, edit `OUTPUT_FILE`:

```python
OUTPUT_FILE = "example/custom.log"
```

To print the report directly to the terminal, set:

```python
OUTPUT_FILE = None
```

---

## GitHub Token

A GitHub token is optional for public repositories.

The default demo repository is public, so the tool can run without setting a token.

For authenticated requests, keep the real token outside the source code. The Python file should only contain the environment variable name:

```python
TOKEN_ENV = "GITHUB_TOKEN"
```

Do not paste a real token into `TOKEN_ENV`.

Bad:

```python
TOKEN_ENV = "github_pat_xxxxxxxxxxxxxxxxx"
```

Good:

```python
TOKEN_ENV = "GITHUB_TOKEN"
```

To set a token for the current terminal session, use one of the commands below.

Linux, macOS, Git Bash, or WSL:

```bash
export GITHUB_TOKEN="your_token_here"
```

Windows PowerShell:

```powershell
$env:GITHUB_TOKEN="your_token_here"
```

After setting the token, run the tool in the same terminal session.

---

## Usage

Run the tool from the project directory:

```bash
python3 repo_inspector.py
```

Expected output:

```text
Report saved to: example/demo.log
Repository: octocat/Hello-World
```

View the generated report:

```bash
cat example/demo.log
```

On Windows PowerShell, view the generated report with:

```powershell
Get-Content example/demo.log
```

---

## Report Format

The generated report has this structure:

```text
# GitHub Repo Inspector Report

Repository: ...
URL: ...
Description: ...
Default branch: ...
Visibility: ...
Stars: ...
Forks: ...
Open issues: ...
License: ...

## File system summary

Files: ...
Folders: ...
Submodules: ...
Total file size: ...

## Languages

...

## Top file extensions

...

## Largest files

...
```

---

## GitHub API Endpoints

The tool uses these GitHub REST API endpoints:

```text
GET /repos/{owner}/{repo}
GET /repos/{owner}/{repo}/languages
GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1
```

| Endpoint | Purpose |
|---|---|
| `/repos/{owner}/{repo}` | Read repository metadata |
| `/repos/{owner}/{repo}/languages` | Read language statistics |
| `/repos/{owner}/{repo}/git/trees/{branch}?recursive=1` | Read the repository file tree |

The recursive tree endpoint allows the tool to count files and folders without cloning the repository.

---

## Notes

The tool does not use command-line arguments.

To change the repository, output file, timeout, retry count, or report size, edit the configuration values at the top of `repo_inspector.py`.

The tool does not clone repositories.

The tool only reads data through the GitHub REST API.

Large repositories may take longer to inspect because the recursive tree response can be large.

---

## Troubleshooting

Common network errors:

```text
Temporary failure in name resolution
Remote end closed connection without response
The read operation timed out
```

Possible fixes:

```text
check the internet connection
restart WSL
increase TIMEOUT
increase RETRIES
try again later
```

For WSL, this command may help:

```powershell
wsl --shutdown
```

For slow network connections, increase:

```python
TIMEOUT = 60
RETRIES = 8
```

---

## Security

Never commit a real GitHub token.

Keep the token outside the source code and read the token through an environment variable.

Recommended `.gitignore` content:

```text
.env
__pycache__/
*.pyc
```

If a token was committed by mistake, revoke the token and create a new token.

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).