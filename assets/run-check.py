import datetime
import json
import re
import subprocess
import sys


def main():
    payload = json.loads(sys.argv[1])
    source = payload['source']

    if 'uri' not in source:
        print('must configure uri', file=sys.stderr)
        sys.exit(1)
    uri = source['uri']

    include_git_heads = True if 'include_git_heads' in source and source['include_git_heads'] == 'true' else False

    result = subprocess.run(['git', 'ls-remote', '--heads', uri], stdout=subprocess.PIPE)
    lines = [line.strip() for line in result.stdout.decode('utf-8').split('\n') if line.strip()]
    branches = {}
    for line in lines:
        branch = line.split()
        branches[branch[0]] = branch[1].removeprefix('refs/heads/')

    filtered_branches = {}
    if 'branch_regex' in source:
        regex = re.compile(source['branch_regex'])
        for head, name in branches.items():
            if regex.match(name):
                filtered_branches[head] = name
    else:
        filtered_branches = branches

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    out_branches = filtered_branches if include_git_heads is True else list(filtered_branches.values())

    version = {
        'branches': json.dumps(out_branches),
        'timestamp': timestamp,
    }

    if 'version' in payload and 'branches' in payload['version']:
        prev_version = payload['version']
        if prev_version['branches'] == version['branches']:
            out_versions = [prev_version]
        else:
            out_versions = [prev_version, version]
    else:
        out_versions = [version]

    print(json.dumps(out_versions))


if __name__ == '__main__':
    main()
