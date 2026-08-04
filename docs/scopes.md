# Scopes

Dj Celery Panel splits its permission checks into **scopes**: named checkpoints passed to `@panel_config.permission_required(scope)`. Every scope inherits the panel-wide `ALLOWED_GROUPS`/`REQUIRE_SUPERUSER` rule by default; a scope only behaves differently once you add an entry for it under `SCOPE_PERMISSIONS` in `DJ_CELERY_PANEL_SETTINGS`.

See the [Permissions and Scopes guide](https://djangocontrolroom.com/guides/control-room-permissions-and-scopes) for the full model.

## Reference

| Scope | Type | Protects | Default behavior |
|---|---|---|---|
| `overview` | View | `index` view: overview of registered and periodic (beat) tasks | Any staff user |
| `workers` | View | `workers` view: list of active Celery workers | Any staff user |
| `worker_detail` | View | `worker_detail` view: a single worker's status, queues, and task state | Any staff user |
| `tasks` | View | `tasks` view: search/filter task execution history | Any staff user |
| `task_detail` | View | `task_detail` view: a single task's args, kwargs, result, and traceback | Any staff user |
| `queues` | View | `queues` view: list of known queues | Any staff user |
| `queue_detail` | View | `queue_detail` view: a single queue's depth, consumers, and exchange config | Any staff user |
| `configuration` | View | `configuration` view: Celery broker/backend/task settings dump | Any staff user |

This panel does not currently register MCP tools, so there are no `agent_*` scopes.

## Example: restrict configuration and task details

```python
DJ_CELERY_PANEL_SETTINGS = {
    # Panel-wide default: any staff member can browse workers/tasks/queues
    'ALLOWED_GROUPS': [],

    'SCOPE_PERMISSIONS': {
        # Configuration can expose broker URLs and other sensitive settings.
        'configuration': {'REQUIRE_SUPERUSER': True},

        # Task detail shows args/kwargs/results — restrict if those may
        # contain PII or secrets.
        'task_detail': {'ALLOWED_GROUPS': ['platform-admins']},
    },
}
```

Any scope not mentioned in `SCOPE_PERMISSIONS` simply falls back to the panel-wide rule, so you only ever need to write down the exceptions.

See [Configuration](configuration.md) for the rest of the panel's settings, including swappable backends.
