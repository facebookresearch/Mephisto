---
sidebar_position: 1
---

# Use the same configs across tasks

As you begin launching many Mephisto tasks, you may find that there are some specific argument options that you frequently use _across_ multiple tasks. Mephisto provides a way to reuse these types of configurations with `profile`s.

Setting up profiles is pretty easy, and makes it so that you don't have to be writing architect and crowdprovider args on every launch:
```
python run_task.py mephisto/architect=heroku mephisto/provider=mturk_sandbox mephisto.provider.requester_name=MY_REQUESTER
```

Instead you can move these common configurations into a file in your `~/.mephisto/hydra_configs/profile` dir. 

With this, you can do something like:
```yaml
# profile/local_testing.yaml
# @package _global_
mephisto:
  architect:
    _architect_type: local
    port: 1234
  provider:
    _provider_type: mock

# profile/internal_sharing.yaml
# @package _global_
mephisto:
  architect:
    _architect_type: heroku
    use_hobby: false
  provider:
    _provider_type: mock

# profile/prelaunch_test.yaml
# @package _global_
mephisto:
  architect:
    _architect_type: heroku
    use_hobby: false
  provider:
    _provider_type: mturk_sandbox
    requester_name: MY_REQUESTER_sandbox

# profile/live_launch.yaml
# @package _global_
mephisto:
  architect:
    _architect_type: heroku
    use_hobby: true
  provider:
    _provider_type: mturk
    requester_name: MY_REQUESTER
```

Then augmenting your launch configs is as easy as doing:
```
python run_task.py +profile=local_testing
...
python run_task.py +profile=live_launch
```

Using `profile` can be an effective way to simplify the configuration for your most common workflows.
