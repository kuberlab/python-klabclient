# python-dealerclient

### Installation

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

### Usage

```bash
# Set token
export DEALER_TOKEN=token
# Or, use your login/password
export DEALER_USERNAME=my@example.com
export DEALER_PASSWORD=mypassword

dealer workspace-list

# See help
dealer --help
```

### Usage as a python library

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
