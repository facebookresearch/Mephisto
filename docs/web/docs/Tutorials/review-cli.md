# Using the Mephisto Review CLI

Once you've [installed Mephisto](/TODO), you have access to the `mephisto` command line utility.

This utility can be used to invoke a review workflow via `$ mephisto review ...`.

## Overview

To review data, you must specify:

1. The actual data to review
2. The visual interface to represent the data
3. If approving/rejecting (as opposed to  exploring), what to do with the results

Here's a sample command:

```shell
cat input.jsonl | mephisto review --json my-review-interface --stdout
```

Here we:

1. Pipe in the contents of `input.jsonl` to the `mephisto review` command. This is our review data as newline separated JSON payloads. (*We also specify the `--json` flag to indicate that this is JSON input as opposed to the default CSV.*)

2. Point to the build location of our review interface. This is a single-page app that implements the `useMephistoReview()` hook to consume data. (*To start with a starter template, you can you `cra-template-mephisto-review`. We will elaborate on this below.*)

3. Specify the output of our approve/reject data. For now we will just print it out to standard output with the `--stdout` flag.

## Create your own interface

The quickest way to create your own review interface is to use the `cra-template-mephisto-review` template with `create-react-app`:

```
npx create-react-app --template mephisto-review my-review-interface
```