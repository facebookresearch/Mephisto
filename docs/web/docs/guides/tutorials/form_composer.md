---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 6
---

# Run form-based tasks

If your task has questionnaire format, you can build it out-of-the box with no custom code, by using our FormComposer task generator. All you need to do is to specify your JSON-based form configuration, and run a few commands.

- Form layout is mobile-screen compatible; it's based on Bootstrap and displays content organized into form sections, fieldsets, fields, etc
- Standard form behaviours include URL presigning (for data security), collapsible form sections, and fields validation
- Optionally, you can customize form behaviour with JS code insertions to enable:
    - custom field validators (e.g. check text against a dictionary of forbidden words)
    - custom field triggers (e.g. toggle a form field based upon value provided in another field)


## Run with docker

To launch a form-based Task from within a Docker container follow these steps:

1. Prepare and validate your config files as described in [FormComposer config files](/docs/guides/how_to_use/form_composer/configuration/setup/) and
[form_composer config command](/docs/guides/how_to_use/form_composer/configuration/form_composer_config_command/) sections

2. Launch your form-based Task (see details in [Running FormComposer task](/docs/guides/how_to_use/form_composer/running/)). For a lcal testing scenario, we will run:

```shell
docker-compose -f docker/docker-compose.dev.yml run \
    --build \
    --publish 8081:8000 \
    --publish 3001:3000 \
    --rm mephisto_dc \
    mephisto form_composer
```

## Access Task units

Once your Task launches, your console will display you URLs like this: `http://<YOUR_DOMAIN>/?worker_id=x&assignment_id=1`.

- If you're doing local testing with `local` architect and `mock` provider, your URLs will start with `http://localhost:3000/`. To access your Task units as a worker, just paste one of these URLs into your browser.
    - _If running with Docker, you will need to replace port `3000` in the console URLs with the remapped port (e.g. for `3001:3000` it will be `3001`)._
- If you're running with a "real" provider, to access your Task units you will need to log into the provider's platform as a worker, and find them there.

## Further Details

Learn more in our FormComposer guide:
- [FormComposer overview](/docs/guides/how_to_use/form_composer/overview/)
- [Run FormComposer tasks](/docs/guides/how_to_use/form_composer/running/)
- [Configure FormComposer tasks](/docs/guides/how_to_use/form_composer/configuration/setup/)
- [Embed FormComposer into custom application](/docs/guides/how_to_use/form_composer/embedding/)
