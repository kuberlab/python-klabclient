import time
import yaml

from klabclient.api import base
from klabclient import exceptions
from klabclient import utils


def build_aware(func):
    def decorator(self, *args, **kwargs):
        if not hasattr(self, 'build'):
            raise exceptions.KuberlabClientException('Task has no build yet')
        return func(self, *args, **kwargs)
    return decorator


class AppTaskPod(base.Resource):
    resource_name = 'AppTaskPod'

    def __str__(self):
        return (
            '<AppTaskPod Name=%s Status=%s>'
            % (self.Name, self.Status)
        )

    def __repr__(self):
        return self.__str__()


class AppTask(base.Resource):
    resource_name = 'AppTask'

    # "app": "21-styles-set",
    # "build": "7",
    # "completed": false,
    # "config": "labels: null\nname: prepare-data\n...",
    # "name": "prepare-data",
    # "serve": null,
    # "start_time": "2017-10-19T13:06:01.543311498Z",
    # "status": "Starting",
    # "stop_time": null,
    # "exitError": "",
    def __init__(self, manager, data):
        super(AppTask, self).__init__(manager, data)
        if hasattr(self, 'config'):
            self.config_raw = self.config
            self.config = yaml.safe_load(self.config_raw)
        if hasattr(self, 'app_config'):
            self.app_config_raw = self.app_config
            self.app_config = yaml.safe_load(self.app_config_raw)

        if not hasattr(self, 'status'):
            self.status = 'undefined'

    def __str__(self):
        if not hasattr(self, 'build'):
            build = None
        else:
            build = self.build

        return (
            '<Task name=%s build=%s status=%s>'
            % (self.name, build, self.status)
        )

    def __repr__(self):
        return self.__str__()

    def _update_attrs(self, new_task):
        if hasattr(new_task, 'build'):
            self.build = new_task.build
            self.status = new_task.status
            self.completed = new_task.completed
            self.start_time = new_task.start_time
            self.stop_time = new_task.stop_time
            self.exitError = getattr(new_task, 'exitError', None)
        return self

    def start(self):
        task = self.manager.create(
            self.workspace, self.app, self.name, self.app_config
        )
        return self._update_attrs(task)

    @build_aware
    def refresh(self):
        task = self.manager.get(
            self.workspace, self.app, self.name, self.build
        )
        return self._update_attrs(task)

    def wait(self, timeout=1800, tick_callback=None):
        @utils.timeout(seconds=timeout)
        @build_aware
        def _wait(self):
            while not self.completed:
                if tick_callback:
                    try:
                        tick_callback(self)
                    except Exception:
                        pass

                time.sleep(3)
                self.refresh()
            return self

        return _wait(self)

    def run(self):
        self.start()
        return self.wait()

    def pods(self):
        return self.manager.get_pods(
            self.workspace, self.app, self.name, self.build
        )

    def logs(self, pod_name):
        return self.manager.get_pod_logs(
            self.workspace, self.app, self.name, self.build, pod_name
        )


class AppTaskManager(base.ResourceManager):
    resource_class = AppTask

    def create(self, workspace, app_name, task, config=None):
        self._ensure_not_empty(
            workspace=workspace,
            app_name=app_name,
            task=task,
        )

        body = {}
        if config:
            body = config

        url = (
            '/workspace/%s/application/%s/build/%s'
            % (workspace, app_name, task)
        )
        return self._create(url, body)

    def list(self, workspace, app_name):
        url = '/workspace/%s/application/%s/tasks' % (workspace, app_name)
        tasks = self._list(url, response_key=None)

        [setattr(t, 'workspace', workspace) for t in tasks]
        return tasks

    def get(self, workspace, app_name, task, build):
        url = (
            '/workspace/%s/application/%s/tasks/%s/build/%s'
            % (workspace, app_name, task, build)
        )
        self._ensure_not_empty(
            workspace=workspace, app=app_name, task=task, build=build
        )

        task = self._get(url)
        task.workspace = workspace
        return task

    def get_pods(self, workspace, app_name, task, build):
        url = (
            '/workspace/%s/application/%s/tasks/%s/build/%s/pods'
            % (workspace, app_name, task, build)
        )
        self._ensure_not_empty(
            workspace=workspace, app=app_name, task=task, build=build
        )

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        return [AppTaskPod(self, p) for p in base.extract_json(resp, None)]

    def get_pod_logs(self, workspace, app_name, task, build, pod):
        url = (
            '/workspace/%s/application/%s/tasks/%s/build/%s/pods/%s/log'
            % (workspace, app_name, task, build, pod)
        )
        self._ensure_not_empty(
            workspace=workspace, app=app_name, task=task, build=build, pod=pod
        )

        resp = self.http_client.get(url)
        if resp.status_code >= 400:
            self._raise_api_exception(resp)

        log = base.extract_json(resp, None)

        return log.get('output')

    def delete(self, workspace, app_name, task, build):
        url = (
            '/workspace/%s/application/%s/tasks/%s/build/%s'
            % (workspace, app_name, task, build)
        )
        self._ensure_not_empty(
            workspace=workspace, app=app_name, task=task, build=build
        )

        return self._delete(url)
