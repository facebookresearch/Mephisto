---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 4
---

# Manually installing Mephisto

We strongly recommend [running Mephisto with Docker](/docs/guides/how_to_use/efficiency_organization/docker/) as we've shown in all included task examples.

If you do need to build it up from scratch (e.g. on a remote server),
follow this provided installation manual.

> NOTE: Currently our instructions include only Ubuntu 24.04 LTS with Python 3.9 and Nodejs 16.
> In the future we will include instructions and support for other systems as well.

## Ubuntu 24.04 LTS

Note that the following steps have already been coded up in
[Dockerfile for Ubuntu 24.04 LTS](https://github.com/facebookresearch/Mephisto/blob/main/docker/dockerfiles/Dockerfile.ubuntu-24.04).
This Dockerfile is not the base Mephisto image,
but rather an example for testing and experimenting.

### 1. Clone Mephisto repository

Download Mephisto code to `<MEPHISTO_REPO_PATH>` directory in your local system.

```shell
cd <MEPHISTO_REPO_PATH>
git clone git@github.com:facebookresearch/Mephisto.git
```


### 2. Prepare system

#### Install system requirements

```shell
apt update -y
apt upgrade -y
apt install software-properties-common keychain curl -y
add-apt-repository ppa:deadsnakes/ppa -y
apt update -y
```

#### Install Python env (Python3.9 and pip), and set default Python version

```shell
apt install wget python3.9 python3.9-dev python3.9-distutils -y
wget https://bootstrap.pypa.io/get-pip.py
python3.9 get-pip.py
update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
```

#### Install JS env (Nodejs and Yarn)

```shell
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" \
    && nvm install 22 \
    && ln -s $(which node) /usr/bin/node \
    && ln -s $(which npm) /usr/bin/npm
npm install -g yarn
```


### 3. Setup Mephisto

#### Install Python requirements

```shell
pip install --upgrade pip
cd <MEPHISTO_REPO_PATH> && pip install -e .
```

#### # Setup Mephisto's directories

```shell
mkdir -p ~/.mephisto
mkdir -p <MEPHISTO_REPO_PATH>/data
mephisto config core.main_data_directory <MEPHISTO_REPO_PATH>/data
```

#### Assert that everything has been set up correctly

```shell
mephisto check
```

---

## Let's get running!

Now that you have your environment set up, you're ready for
[Running your first task](/docs/guides/tutorials/first_task/).
