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

    result = subprocess.run(['git', 'ls-remote', '--heads', uri], stdout=subprocess.PIPE)
    lines = [line.strip() for line in result.stdout.decode('utf-8').split('\n') if line.strip()]
    branches = [line.split()[1].removeprefix('refs/heads/') for line in lines]

    if 'branch_regex' in source:
        regex = re.compile(source['branch_regex'])
        branches = [branch for branch in branches if regex.match(branch)]

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    version = {
        'branches': json.dumps(branches),
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
