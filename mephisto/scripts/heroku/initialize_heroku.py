#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from mephisto.abstractions.architects.heroku_architect import HerokuArchitect


def main():
    """
    Force Mephisto to check heroku architect's credentials.
    If this succeeds, then it's a no-op. If it fails,
    it will print setup instructions
    """
    print(
        "Assessing if heroku credentials are set. "
        "If this fails, follow the provided instructions."
    )
    path, creds = HerokuArchitect.get_user_identifier()
    print("Successfully identified a logged in heroku user.")


if __name__ == "__main__":
    main()
