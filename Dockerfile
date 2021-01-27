# Using the -slim version below for minimal size. You may want to
# remove -slim, or switch to -alpine if encountering issues

FROM nikolaik/python-nodejs:python3.9-nodejs15-slim

COPY . /mephisto
RUN mkdir ~/.mephisto

# Write the mephisto config file manually for now to avoid prompt.
# For bash-style string $ expansion for newlines,
# we need to switch the shell to bash:
SHELL ["/bin/bash", "-c"]
RUN echo $'core: \n  main_data_directory: /mephisto/data' >> ~/.mephisto/config.yml

RUN cd /mephisto && pip install -e .
CMD mephisto check
