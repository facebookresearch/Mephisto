---
# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

sidebar_position: 6
---

# Form rendering callbacks

During rendering of a Task in the browser, we may send calls to the server-side for additional data. In Mephisto, API views servicing such requests are called "remote procedures".


## Presigned S3 URLs

An example of a remote procedure that gets called during the initial form loading, is `getPresignedUrl` and `getMultiplePresignedUrls` functions. These functions allow to generate short-lived S3 URLs, in order to limit exposure of sensitive resources.

The below command auto-generates config token values that presign themselves during rendering of the Task page:

```
mephisto form_composer config --update-file-location-values "https://s3.amazonaws.com/..." --use_presigned_urls
```

This is how URL pre-signing works:
- When a worker opens the Task page and the form HTML is generated, it will contain so-called "procedure tokens", i.e. token values that look like this: `{{getMultiplePresignedUrls(<S3_FILE_URL>)}}`
    - the "wrapper" part of a procedure token is the name of a Javascript function that will render itself dynamically (e.g. by calling some remote API to receive additional data)
    - the argument part is the argument value provided suring the function call
- As soon as the form HTML is in place, the remote procedure gets called
- Mephisto's predefined remote procedure generates presigned URL, and its expiration starts ticking

Presigned S3 URLs use the following environment variables:
- Required: valid AWS credentials: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`
  (`form_composer config` command)
- Optional: URL expiration time `S3_URL_EXPIRATION_MINUTES` (if missing the default value is 60 minutes)


## Custom callbacks

You can write your own remote procedures. A good place to start is looking at how S3 URL presigning is implemented in the `examples/form_composer_demo` example project.
