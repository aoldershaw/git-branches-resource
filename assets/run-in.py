import json
import re
import sys


def main():
    payload = json.loads(sys.argv[1])
    branches = json.loads(payload['version']['branches'])

    source = payload['source']

    branch_regexes = []
    if 'branch_regexes' in source:
        branch_regexes = [re.compile(regex) for regex in source['branch_regexes']]

    elif 'branch_regex' in source:
        branch_regexes = [re.compile(source['branch_regex'])]

    if branch_regexes:
        output = []
        for branch in branches:
            for regex in branch_regexes:
                if regex.fullmatch(branch):
                    output.append({'name': branch, 'groups': regex.fullmatch(branch).groupdict()})
                    break
    else:
        output = [{'name': branch} for branch in branches]

    print(json.dumps(output))


if __name__ == '__main__':
    main()
