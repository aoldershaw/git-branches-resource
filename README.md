# Git Branches Resource

Tracks the set of branches that exist in a [git](http://git-scm.com/)
repository.

This resource differs from [vito/git-branches-resource](https://github.com/vito/git-branches-resource) in a few ways:

* The list of branches is emitted as a JSON file so that it can be ingested by
  the `load_var` step
* Branches can be filtered by a regular expression (`source.branch_regex`)
* More authentication methods are supported

See the [#example](#example) for an example of how to use this resource to
support multi-branch workflows in Concourse.

## Installation

Add the following `resource_types` entry to your pipeline:

```yaml
---
resource_types:
- name: git-branches
  type: registry-image
  source: {repository: aoldershaw/git-branches-resource}
```

## Source Configuration

* `uri`: *Required.* The location of the repository.

* `private_key`: *Optional.* Private key to use when pulling/pushing.
    Example:
    ```
    private_key: |
      -----BEGIN RSA PRIVATE KEY-----
      MIIEowIBAAKCAQEAtCS10/f7W7lkQaSgD/mVeaSOvSF9ql4hf/zfMwfVGgHWjj+W
      <Lots more text>
      DWiJL+OFeg9kawcUL6hQ8JeXPhlImG6RTUffma9+iGQyyBMCGd1l
      -----END RSA PRIVATE KEY-----
    ```

* `private_key_user`: *Optional.* Enables setting User in the ssh config.

* `private_key_passphrase`: *Optional.* To unlock `private_key` if it is protected by a passphrase.

* `forward_agent`: *Optional* Enables ForwardAgent SSH option when set to true. Useful when using proxy/jump hosts. Defaults to false.

* `username`: *Optional.* Username for HTTP(S) auth when pulling/pushing.
  This is needed when only HTTP/HTTPS protocol for git is available (which does not support private key auth)
  and auth is required.

* `password`: *Optional.* Password for HTTP(S) auth when pulling/pushing.

* `skip_ssl_verification`: *Optional.* Skips git ssl verification by exporting
  `GIT_SSL_NO_VERIFY=true`.

* `branch_regex`: *Optional.* If specified, the resource will only detect
  branches that have a name matching the expression. Patterns are
  [grep](https://www.gnu.org/software/grep/manual/grep.html) compatible
  (extended matching enabled, matches entire lines only).

* `git_config`: *Optional*. If specified as (list of pairs `name` and `value`)
  it will configure git global options, setting each name with each value.

  This can be useful to set options like `credential.helper` or similar.

  See the [`git-config(1)` manual page](https://www.kernel.org/pub/software/scm/git/docs/git-config.html)
  for more information and documentation of existing git options.

* `https_tunnel`: *Optional.* Information about an HTTPS proxy that will be used to tunnel SSH-based git commands over.
  Has the following sub-properties:
  * `proxy_host`: *Required.* The host name or IP of the proxy server
  * `proxy_port`: *Required.* The proxy server's listening port
  * `proxy_user`: *Optional.* If the proxy requires authentication, use this username
  * `proxy_password`: *Optional.* If the proxy requires authenticate,
      use this password

### Example

This resource can be used to support multi-branch workflows (by setting a
pipeline for each branch). This approach requires two pipeline templates.

1. There is one "parent" pipeline that monitors the list of branches in a
   repository, and sets a group of "child" pipelines (one for each matching
   branch).
2. There is one "child" pipeline for each matching branch. It would be typical
   for each child pipeline to track the commits to the corresponding branch.

For this example, assume you have a resource named `ci`, a repo which contains
the following pipeline files:

`ci/pipelines/parent.yml`
```yaml
resource_types:
- name: git-branches
  type: registry-image
  source:
    repository: aoldershaw/git-branches-resource

resources:
- name: release-branches
  type: git-branches
  source:
    uri: git@github.com:concourse/concourse.git
    branch_regex: release/.*
    private_key: |
      -----BEGIN RSA PRIVATE KEY-----
      MIIEowIBAAKCAQEAtCS10/f7W7lkQaSgD/mVeaSOvSF9ql4hf/zfMwfVGgHWjj+W
      <Lots more text>
      DWiJL+OFeg9kawcUL6hQ8JeXPhlImG6RTUffma9+iGQyyBMCGd1l
      -----END RSA PRIVATE KEY-----

- name: ci
  type: git
  source:
    uri: https://github.com/concourse/ci

jobs:
- name: update-branch-pipelines
  plan:
  - get: ci
  - get: release-branches
    trigger: true
  - load_var: branches
    file: release-branches/branches.json
  - across:
    - var: branch
      values: ((.:branches))
    set_pipeline: my-repo
    file: ci/pipelines/child.yml
    instance_vars: {branch: ((.:branch))}
```

`ci/pipelines/child.yml`
```yaml
resources:
- name: repo
  type: git
  source:
    uri: git@github.com:concourse/concourse.git
    branch: ((branch))
    private_key: |
      -----BEGIN RSA PRIVATE KEY-----
      MIIEowIBAAKCAQEAtCS10/f7W7lkQaSgD/mVeaSOvSF9ql4hf/zfMwfVGgHWjj+W
      <Lots more text>
      DWiJL+OFeg9kawcUL6hQ8JeXPhlImG6RTUffma9+iGQyyBMCGd1l
      -----END RSA PRIVATE KEY-----

- name: test
  plan:
  - get: repo
    trigger: true
  - task: unit-test
    config:
      platform: linux
      image_resource:
        type: registry-image
        source: {repository: alpine}
      inputs:
      - name: repo
      run:
        path: /bin/sh
        args:
          - -e
          - |
            echo "running some tests for branch ((branch))!"
```

## Behavior

### `check`: Check for changes to the branch set.

The list of remote branches are enumerated, possibly filtered by the
`branch_regex`, and compared to the existing set of branches. If any branches
are new or removed, a new version is emitted.

### `in`: Produce the version's info as files.

Produces the following file based on the version being fetched:

* `branches.json`: A file containing the list of current branches, encoded as a
  JSON array of strings.


### `out`: No-op.

*Not implemented.*
