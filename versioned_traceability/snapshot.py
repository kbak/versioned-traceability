import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .common import CheckError, canonical, digest, relative_path


def git(repo, *args, data=None):
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            input=data,
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CheckError(f"Cannot run Git: {exc}") from exc
    if result.returncode:
        raise CheckError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def repository(path):
    repo = path.resolve(strict=True)
    root = Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel")).strip()).resolve()
    if repo != root:
        raise CheckError(f"--repo must name the Git repository root: {root}")
    return repo


def resolve_commit(repo, ref):
    return (
        git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").decode().strip()
    )


@dataclass
class Snapshot:
    root: Path
    commit: str
    kind: str
    manifest: list

    @property
    def sha256(self):
        return digest(canonical(self.manifest))

    def identity(self):
        return {
            "kind": self.kind,
            "commit": self.commit,
            "sha256": self.sha256,
            "file_count": len(self.manifest),
        }


def put_file(root, name, mode, data):
    relative_path(name)
    if mode not in ("100644", "100755"):
        raise CheckError(
            f"Unsupported Git entry {name} ({mode}); symlinks and submodules are not supported yet"
        )
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    target.chmod(0o755 if mode == "100755" else 0o644)
    return {"path": name, "mode": mode, "sha256": digest(data)}


def worktree_entries(repo):
    index = git(repo, "ls-files", "--stage", "-z").split(b"\0")
    for entry in filter(None, index):
        metadata, name = entry.split(b"\t", 1)
        mode, _, stage = metadata.split()
        if stage != b"0":
            raise CheckError("Resolve Git merge conflicts before checking")
        if mode not in (b"100644", b"100755"):
            raise CheckError(f"Unsupported Git entry: {os.fsdecode(name)} ({mode.decode()})")
    names = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    entries = []
    for name in sorted(set(filter(None, names.split(b"\0")))):
        relative = os.fsdecode(name)
        relative_path(relative)
        path = repo / relative
        if not path.resolve().is_relative_to(repo):
            raise CheckError(f"Source escapes repository: {relative}")
        # Reject symlink parents as well as symlink files.
        if any(
            parent.is_symlink()
            for parent in [path, *path.parents]
            if parent != repo and parent.is_relative_to(repo)
        ):
            raise CheckError(f"Symlinks are not supported: {relative}")
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue  # A tracked deletion is represented by absence from the snapshot.
        if not stat.S_ISREG(info.st_mode):
            raise CheckError(f"Expected a regular source file: {relative}")
        mode = "100755" if info.st_mode & stat.S_IXUSR else "100644"
        entries.append((relative, mode, path.read_bytes()))
    return entries


def snapshot(repo, selection, destination):
    destination.mkdir()
    commit = resolve_commit(repo, "HEAD" if selection == "worktree" else selection)
    if selection == "worktree":
        entries = worktree_entries(repo)
    else:
        records = []
        for record in filter(None, git(repo, "ls-tree", "-rz", "--full-tree", commit).split(b"\0")):
            header, name = record.split(b"\t", 1)
            mode, kind, oid = header.split()
            if kind != b"blob" or mode not in (b"100644", b"100755"):
                raise CheckError(f"Unsupported Git entry: {os.fsdecode(name)} ({mode.decode()})")
            records.append((os.fsdecode(name), mode.decode(), oid))
        # Read Git objects, not git archive: export-ignore/export-subst must not change checked bytes.
        blobs = git(
            repo, "cat-file", "--batch", data=b"".join(oid + b"\n" for _, _, oid in records)
        )
        entries = []
        offset = 0
        for name, mode, oid in records:
            end = blobs.index(b"\n", offset)
            actual_oid, kind, length = blobs[offset:end].split()
            size = int(length)
            if actual_oid != oid or kind != b"blob":
                raise CheckError("Unexpected Git object response")
            entries.append((name, mode, blobs[end + 1 : end + 1 + size]))
            offset = end + size + 2
    manifest = sorted((put_file(destination, *entry) for entry in entries), key=lambda f: f["path"])
    return Snapshot(
        destination, commit, "worktree" if selection == "worktree" else "commit", manifest
    )


def changed_source(snap):
    changed = []
    for entry in snap.manifest:
        path = snap.root / entry["path"]
        try:
            mode = "100755" if path.stat().st_mode & stat.S_IXUSR else "100644"
            if (
                path.is_symlink()
                or digest(path.read_bytes()) != entry["sha256"]
                or mode != entry["mode"]
            ):
                changed.append(entry["path"])
        except OSError:
            changed.append(entry["path"])
    return changed


def archive_snapshot(source, commit, destination):
    """Capture a caller-supplied source archive; commit attribution is external."""
    source = source.resolve(strict=True)
    destination.mkdir()
    manifest = []
    for parent, directories, names in os.walk(source):
        directories[:] = [name for name in directories if name != ".git"]
        for name in directories + names:
            path = Path(parent) / name
            if path.is_symlink():
                raise CheckError(f"Symlinks are not supported: {path.relative_to(source)}")
        for name in names:
            if name == ".git":
                continue
            path = Path(parent) / name
            info = path.stat()
            if not stat.S_ISREG(info.st_mode):
                raise CheckError(f"Expected a regular source file: {path.relative_to(source)}")
            mode = "100755" if info.st_mode & stat.S_IXUSR else "100644"
            manifest.append(
                put_file(destination, path.relative_to(source).as_posix(), mode, path.read_bytes())
            )
    return Snapshot(
        destination, commit, "archive", sorted(manifest, key=lambda entry: entry["path"])
    )
