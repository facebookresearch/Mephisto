



# Architects


Architects contain the logic surrounding deploying a server that workers will be able to access.
## mock


  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|server_type|str|node|None|None|False|
|server_source_path|str|???|Optional path to a prepared server directory containing everything needed to run a server of the given type. Overrides server type. |None|False|
|should_run_server|bool|False|Addressible location of the server|None|False|
|port|str|3000|Port to launch the server on|None|False|

## local


  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|server_type|str|node|None|None|False|
|server_source_path|str|???|Optional path to a prepared server directory containing everything needed to run a server of the given type. Overrides server type. |None|False|
|hostname|str|localhost|Addressible location of the server|None|False|
|port|str|3000|Port to launch the server on|None|False|

## heroku


  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|server_type|str|node|None|None|False|
|server_source_path|str|???|Optional path to a prepared server directory containing everything needed to run a server of the given type. Overrides server type. |None|False|
|use_hobby|bool|False|Launch on the Heroku Hobby tier|None|False|
|heroku_team|unknown|???|Heroku team to use for this launch|None|False|
|heroku_app_name|unknown|???|Heroku app name to use for this launch|None|False|
|heroku_config_args|unknown|{}|str:str dict containing all heroku config variables to set for the app|None|False|

## ec2


  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|server_type|str|node|None|None|False|
|server_source_path|str|???|Optional path to a prepared server directory containing everything needed to run a server of the given type. Overrides server type. |None|False|
|instance_type|str|t2.micro|Instance type to run router|None|False|
|subdomain|str|The task name defined in your task's hydra config|Subdomain name for routing|None|False|
|profile_name|str|???|Profile name for deploying an ec2 instance|None|False|
