import os
import sys
import pathlib
import datetime
import pygit2 as pygit2


def find_toplevel(path, last=None):
    path = pathlib.Path(path).absolute()

    if path == last:
        return None
    if (path / '.git').is_dir():
        return path

    return find_toplevel(path.parent, last=path)


def add_files_to_commit(repo, string_in_file):
    for file in repo.index.diff_to_workdir():
        print(file.delta.old_file.path)
        if string_in_file in file.delta.old_file.path:
            repo.index.add(f'{file.delta.old_file.path}')
            repo.index.write()
    for file in repo.diff('HEAD', cached=True):
        print(file.delta.old_file.path)
        if string_in_file in file.delta.old_file.path:
            repo.index.add(f'{file.delta.old_file.path}')
            repo.index.write()


def git_commit(repo):
    tree = repo.index.write_tree()
    parent, ref = repo.resolve_refish(refish=repo.head.name)

    repo.create_commit(
        ref.name,
        repo.default_signature,
        repo.default_signature,
        f"GitRateWatcher commit on {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d - %H:%M:%S')}",
        tree,
        [parent.oid],
    )


def git_push(branch_name='master'):
    venv_activate_command = f'{os.path.join(os.path.dirname(sys.executable))}\\activate.bat'
    os.system(f'{venv_activate_command} & git push origin {branch_name}')


def git_commit_and_push(string_in_file, branch_name='master', repo_path=None):
    toplevel = repo_path or find_toplevel('../../../../..')
    repo = pygit2.Repository(str(toplevel)) if toplevel is not None else None

    if repo:
        add_files_to_commit(repo, string_in_file)
        git_commit(repo)
        git_push(branch_name)


if __name__ == '__main__':
    git_commit_and_push('qqq')
