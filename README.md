# Easy config
Easy to use config processing based on yaml-files configuration. Allows hierarchical storage of configuration parameters, local storage for secrets and local parameters, validation of local and default configuration files validation.

# Usage

Simple example:
```
from requests import post
from src.utils.config inmport Config

cfg = Config()
post(cfg.api_key, json={'user_id': 1})
```

In this example api_key is a secret. So, the following files are recoomended to have:
```
# configs/config-default.yaml
api_key:  # api key for the external service
```
This should be tracked by git. So called global config files.
```
# configs/config.yaml
api_key: some-very-secret-key
```
This should **not** be tracked by git. So called local config files. Similar to config files in git version system.

# Advantages

+ You can have comments which describes your configuration parameters due to capabilities of yaml-files.  
+ You can make hierarchy of configurations due to capabilities of yaml-files.  
+ You can make references to another part of configuration due to capabilities of yaml-files.  
+ `Config` always validates that global and local config files have same structure in terms of dictionary.  

