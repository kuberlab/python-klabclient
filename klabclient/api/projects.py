
from klabclient.api import base


class Project(base.Resource):
    resource_name = 'Project'

    # "ID": "4121",
    # "Name": "go-kuberlab",
    # "DisplayName": "go.kuberlab",
    # "Description": "",
    # "Environment": "master",
    # "RepositoryID": "2041",
    # "RepositoryURL": "https://github.com/kuberlab/go.kuberlab",
    # "RepositoryDir": "/"


class ProjectManager(base.ResourceManager):
    resource_class = Project

    def create(self, workspace, name, display_name=None,
               env=None, repo_url=None, repo_dir=None):
        self._ensure_not_empty(
            workspace=workspace,
            name=name,
            env=env,
            repo_url=repo_url
        )

        if not display_name:
            display_name = name

        body = {
            'Name': name,
            'DisplayName': display_name,
            'Environment': env,
            'RepositoryURL': repo_url,
            'RepositoryDir': repo_dir if repo_dir else '/'
        }

        return self._create(
            '/workspace/%s/projects' % workspace,
            body,
        )

    def update(self, workspace, name, display_name=None,
               env=None, repo_url=None, repo_dir=None):
        self._ensure_not_empty(id=id, name=name)

        self._ensure_not_empty(
            workspace=workspace,
            name=name,
            env=env,
            repo_url=repo_url
        )

        if not display_name:
            display_name = name

        body = {
            'Name': name,
            'DisplayName': display_name,
            'Environment': env,
            'RepositoryURL': repo_url,
            'RepositoryDir': repo_dir if repo_dir else '/'
        }

        return self._update(
            '/workspace/%s/projects/%s' % (workspace, name),
            body
        )

    def list(self, workspace):
        url = '/workspace/%s/projects' % workspace
        return self._list(url, response_key=None)

    def get(self, workspace, name):
        self._ensure_not_empty(workspace=workspace, name=name)

        return self._get('/workspace/%s/projects/%s' % (workspace, name))

    def delete(self, workspace, name):
        self._ensure_not_empty(workspace=workspace, name=name)

        self._delete('/workspace/%s/projects/%s' % (workspace, name))
