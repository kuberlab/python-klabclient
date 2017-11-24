# python-dealerclient

## Installation

Developer installation:

```bash
git clone https://github.com/kuberlab/python-dealerclient
cd python-dealerclient
pip install -e .
```
    
User installation:

```bash
pip install git+https://github.com/kuberlab/python-dealerclient.git
```

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
export DEALER_TOKEN=token
# Or, use your login/password
export DEALER_USERNAME=my@example.com
export DEALER_PASSWORD=mypassword
```

#### Call CLI or see help to take a look on a command list:

```bash
dealer workspace-list

# See help
dealer --help
```

## App installation example

See how to install a simple app - [App installation](App_installation.md)

**Note**: Priority for auth parameters: CLI parameters, Env variables, config values.

## Usage as a python library

```python
from dealerclient.api import client

# Init session
ses = client.create_session(token='token') # Pick up default base_url
# Or, use username and password
# ses = client.create_session(username='username', password='password') # Pick up default base_url

dealer = client.Client(session=ses) # Pick up default dealer_url

workspaces = dealer.workspaces.list()
# Print all workspace names
print([w.Name for w in workspaces])
```
