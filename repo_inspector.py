import http.client
import json
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

# CONFIG
REPOSITORY = "octocat/Hello-World"
OUTPUT_FILE = "example/demo.log"

TIMEOUT = 30
RETRIES = 5

TOP_EXTENSIONS = 10
TOP_FILES = 10

BASE_URL = "https://api.github.com"
TOKEN_ENV = "GITHUB_TOKEN"

def request_json(path):
    url = BASE_URL + path
    token = os.getenv(TOKEN_ENV)
    last_error = None

    for attempt in range(1, RETRIES + 1):
        try:
            request = urllib.request.Request(url)
            request.add_header("Accept", "application/vnd.github+json")
            request.add_header("User-Agent", "github-repo-inspector")

            if token:
                request.add_header("Authorization", f"Bearer {token}")

            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                data = response.read().decode("utf-8")
                return json.loads(data)

        except urllib.error.HTTPError as error:
            message = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API error {error.code}: {message}") from error

        except (
            urllib.error.URLError,
            TimeoutError,
            socket.timeout,
            ConnectionResetError,
            http.client.RemoteDisconnected,
            http.client.IncompleteRead,
        ) as error:
            last_error = error

            if attempt < RETRIES:
                time.sleep(attempt * 2)

    raise RuntimeError(f"Network error after {RETRIES} retries: {last_error}")


def parse_repository(value):
    value = value.strip()

    if value.startswith("https://github.com/"):
        value = value.removeprefix("https://github.com/").strip("/")

    parts = value.split("/")

    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError("Repository must be in owner/repo format")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")

    return owner, repo


def format_size(size):
    size = float(size)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def analyze_tree(tree):
    files = []
    folders = []
    submodules = []

    for item in tree.get("tree", []):
        item_type = item.get("type")

        if item_type == "blob":
            files.append(item)
        elif item_type == "tree":
            folders.append(item)
        elif item_type == "commit":
            submodules.append(item)

    extensions = Counter()
    largest_files = []
    total_size = 0

    for item in files:
        path = item.get("path", "")
        size = item.get("size", 0)
        extension = Path(path).suffix.lower() or "(no extension)"

        total_size += size
        extensions[extension] += 1
        largest_files.append((path, size))

    largest_files.sort(key=lambda item: item[1], reverse=True)

    return {
        "files": len(files),
        "folders": len(folders),
        "submodules": len(submodules),
        "total_size": total_size,
        "extensions": extensions.most_common(TOP_EXTENSIONS),
        "largest_files": largest_files[:TOP_FILES],
        "truncated": tree.get("truncated", False),
    }


def build_language_report(languages):
    if not languages:
        return ["No language data found."]

    lines = []
    total = sum(languages.values())

    for name, size in sorted(languages.items(), key=lambda item: item[1], reverse=True):
        percent = size / total * 100 if total else 0
        lines.append(f"- {name}: {format_size(size)} ({percent:.2f}%)")

    return lines


def build_extension_report(tree_info):
    if not tree_info["extensions"]:
        return ["No files found."]

    return [
        f"- {extension}: {count}"
        for extension, count in tree_info["extensions"]
    ]


def build_largest_file_report(tree_info):
    if not tree_info["largest_files"]:
        return ["No files found."]

    return [
        f"- {path}: {format_size(size)}"
        for path, size in tree_info["largest_files"]
    ]


def build_report(repository, repo_info, languages, tree_info):
    license_info = repo_info.get("license")
    license_name = license_info.get("name") if license_info else "No license"

    lines = [
        "# GitHub Repo Inspector Report",
        "",
        f"Repository: {repository}",
        f"URL: {repo_info.get('html_url')}",
        f"Description: {repo_info.get('description')}",
        f"Default branch: {repo_info.get('default_branch')}",
        f"Visibility: {repo_info.get('visibility')}",
        f"Stars: {repo_info.get('stargazers_count')}",
        f"Forks: {repo_info.get('forks_count')}",
        f"Open issues: {repo_info.get('open_issues_count')}",
        f"License: {license_name}",
        "",
        "## File system summary",
        "",
        f"Files: {tree_info['files']}",
        f"Folders: {tree_info['folders']}",
        f"Submodules: {tree_info['submodules']}",
        f"Total file size: {format_size(tree_info['total_size'])}",
    ]

    if tree_info["truncated"]:
        lines.extend([
            "",
            "Warning: GitHub returned a truncated tree. The result may be incomplete.",
        ])

    lines.extend([
        "",
        "## Languages",
        "",
        *build_language_report(languages),
        "",
        "## Top file extensions",
        "",
        *build_extension_report(tree_info),
        "",
        "## Largest files",
        "",
        *build_largest_file_report(tree_info),
    ])

    return "\n".join(lines)


def inspect_repository(repository):
    owner, repo = parse_repository(repository)
    full_name = f"{owner}/{repo}"

    repo_info = request_json(f"/repos/{full_name}")
    languages = request_json(f"/repos/{full_name}/languages")

    branch = repo_info.get("default_branch", "main")
    encoded_branch = urllib.parse.quote(branch, safe="")
    tree = request_json(f"/repos/{full_name}/git/trees/{encoded_branch}?recursive=1")

    tree_info = analyze_tree(tree)

    return build_report(full_name, repo_info, languages, tree_info)


def save_report(path, content):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main():
    report = inspect_repository(REPOSITORY)

    if OUTPUT_FILE:
        save_report(OUTPUT_FILE, report)
        print(f"Report saved to: {OUTPUT_FILE}")
        print(f"Repository: {REPOSITORY}")
    else:
        print(report)


if __name__ == "__main__":
    main()