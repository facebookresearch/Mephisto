---

# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 1
---

# 10-minute Quickstart

1. Install Docker and Docker Compose following their [official documentation](https://docs.docker.com/get-docker/)
2. Clone [Mephisto repository](https://github.com/facebookresearch/Mephisto) with command:
    ```shell
    git clone https://github.com/facebookresearch/Mephisto.git
    ```
3. Go into repo directory:
    ```shell
    cd <repo_path>
    ```
4. Run you first example (a simple form-based task):
    ```shell
    docker-compose -f docker/docker-compose.dev.yml run \
      --build \
      --publish 3001:3000 \
      --rm mephisto_dc \
      python /mephisto/examples/form_composer_demo/run_task.py
    ```
5. After the script finishes building, in your console output you will see URLs like this: `localhost:3000/?worker_id=x&assignment_id=1`. Each URL represents a unit of your Task. Copy them one-by-one into your browser, changing port from `3000` to `3001`.
6. After completing all units, you will see your task automatically shut down
7. Now we are ready to review Task results. Run command:
    ```shell
    docker-compose -f docker/docker-compose.dev.yml run \
        --build \
        --publish 8081:8000 \
        --rm mephisto_dc \
        mephisto review_app --host 0.0.0.0 --port 8000
    ```
and open TaskReview app in your browser at [http://localhost:8081](http://localhost:8081)

8. Click on your Task name, and review the task units (that you have just completed yourself earlier).

Congratulations - you have just run and reviewed your very first task!

---

## Next Steps

To understand how to customize Mephisto to your specific needs, we recommend these chapters:

- [Running your first task](/docs/guides/tutorials/first_task/)
- [Reviewing task results](/docs/guides/tutorials/review_app/)
- [Prolific overview](/docs/guides/how_to_use/providers/prolific/intro/)
