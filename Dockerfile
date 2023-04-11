# Using the -slim version below for minimal size. You may want to
# remove -slim, or switch to -alpine if encountering issues
ARG BASE_TAG=python3.9-nodejs15-slim
ARG BASE_IMAGE=nikolaik/python-nodejs:$BASE_TAG

FROM $BASE_IMAGE

# ec2 architect requires `ssh-keygen` util, so we need to install it.
# Firstly, remove `yarn` repo as it causes error that stops building a container. Error:
# (Error: The repository 'https://dl.yarnpkg.com/debian stable InRelease' is not signed)
RUN rm /etc/apt/sources.list.d/yarn.list
RUN apt update
RUN apt install keychain -y

COPY . /mephisto
RUN mkdir ~/.mephisto

# Create the main Mephisto data directory
RUN mkdir /mephisto/data

# Write the mephisto config file manually for now to avoid prompt.
# For bash-style string $ expansion for newlines,
# we need to switch the shell to bash:
SHELL ["/bin/bash", "-c"]
RUN echo $'core: \n  main_data_directory: /mephisto/data' >> ~/.mephisto/config.yml

# Upgrade pip so we can use the pyproject.toml configuration
# without raising an error
RUN pip install --upgrade pip
RUN cd /mephisto && pip install -e .
RUN mephisto check # Run mephisto check so a mock requester gets created
CMD mephisto check
