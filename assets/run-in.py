import json
import re
import sys


def main():
    payload = json.loads(sys.argv[1])
    branches = json.loads(payload["version"]["branches"])

    source = payload["source"]
    include_git_heads = (
        True
        if "include_git_heads" in source and source["include_git_heads"] == "true"
        else False
    )

    if "branch_regex" in source:
        regex = re.compile(source["branch_regex"])
        if include_git_heads:
            output = [
                {
                    "name": branch,
                    "head": head,
                    "groups": regex.match(branch).groupdict(),
                }
                for head, branch in branches.items()
            ]
        else:
            output = [
                {"name": branch, "groups": regex.match(branch).groupdict()}
                for branch in branches
            ]
    else:
        if include_git_heads:
            output = [
                {"name": branch, "head": head} for head, branch in branches.items()
            ]
        else:
            output = [{"name": branch} for branch in branches]

    print(json.dumps(output))


if __name__ == "__main__":
    main()
