# Using Docker

Some users prefer to keep Mephisto entirely contained. Docker is one option for being able to do this.

```bash
# Build the docker image and tag with name 'mephisto'
$ docker build -t mephisto . 

# By default, the container just runs `mephisto check`:
$ docker run mephisto
Mephisto seems to be set up correctly.

# You can also bind ports and pass in shell commands, e.g. to run
# a task directly from the container
$ docker run -p 3000:3000 mephisto bash -c 'cd mephisto/examples/simple_static_task && python static_test_script.py'

```
By default, Mephisto run data will be stored at `/mephisto/data` within the container.
