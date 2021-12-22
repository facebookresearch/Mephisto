# Mephisto Fallback server
The goal of this server is to catch events from requests trying to hit a Mephisto task server that is no longer running.

Any access from any subdomain will be provided the error page, and we log the access domain as well as path params with a timestamp.

### Viewing logs
Access to the path `view_logs` with the url param `access_key` set to the same key as is present in the server's `access_key.txt` file will instead return a json of all of the logged events. You can provide an optional `timestamp` parameter to only return events after that timestamp.