# python-klabclient

## Installation

Developer installation:

```bash
git clone https://github.com/kuberlab/python-klabclient
cd python-klabclient
pip install -e . 
```
* for MacOS add --ignore-installed six at the end of the command line
    
User installation:

```bash
pip install python-klabclient
```
* for MacOS add --ignore-installed six at the end of the command line


Install in virtual environment:


```bash
virtualenv venv
cd venv
bin/pip install python-klabclient
```

* `klab` console command will be accessed from `venv/bin/klab` path.


## Uninstall:

```bash
pip uninstall python-klabclient
```

* Also, if it is required, delete file `~/.kuberlab/config`.

## Usage

#### Use config for auth (default location is *~/.kuberlab/config*)

```bash
touch ~/.kuberlab/config
cat << EOF >> ~/.kuberlab/config
base_url: https://go.kuberlab.com/api/v0.2
token: <user-token>
EOF
```

**Note**: Refer to [Config example](config.yaml.example) to see all possible values.

#### Use environment variables

```bash
# Set token
export KUBERLAB_TOKEN=token
# Or, use your login/password
export KUBERLAB_USERNAME=my@example.com
export KUBERLAB_PASSWORD=mypassword
```

#### Call CLI or see help to take a look on a command list:

```bash
klab workspace-list

# See help
klab --help
```

## App installation example

See how to install a simple app - [App installation](App_installation.md)

**Note**: Priority for auth parameters: CLI parameters, Env variables, config values.

## Usage as a python library

```python
from klabclient.api import client

# Init session
ses = client.create_session(token='token') # Pick up default base_url
# Or, use username and password
# ses = client.create_session(username='username', password='password') # Pick up default base_url

klab = client.Client(session=ses) # Pick up default klab_url

workspaces = klab.workspaces.list()
# Print all workspace names
print([w.Name for w in workspaces])
```
