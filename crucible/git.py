import popen2
import subprocess

def diff(command):
    pr = subprocess.Popen(['/usr/bin/git', 'diff', command],
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           )
    (out, error) = pr.communicate()
    if error:
        raise Exception(error)
    return out

def show(command):
    pr = subprocess.Popen(['/usr/bin/git', 'show', command],
           stdout=subprocess.PIPE,
           stderr=subprocess.PIPE,
           )
    (out, error) = pr.communicate()
    if error:
        raise Exception(error)
    commits = []
    from collections import defaultdict
    commit = defaultdict(lambda: "")
    ignoretext = False
    for line in out.split("\n"):
        if line.startswith("commit "):
            if commit["commit"]:
                commits.insert(0, commit)
                commit = defaultdict(lambda: "")
            commit["commit"] = line[7:]
            ignoretext = True
        elif line.startswith("diff "):
            ignoretext = False
        if not ignoretext:
            commit["patch"] += line + "\n"
    commits.insert(0, commit)
    return commits
