<!---
  Copyright (c) Meta Platforms and its affiliates.
  This source code is licensed under the MIT license found in the
  LICENSE file in the root directory of this source tree.
-->

# Abstraction Subcomponents

This folder holds subcomponents of the core abstractions that are self-contained, but are built as a layer upon the data model. Each can be imported from its abstraction (like `from mephisto.abstractions.blueprint import TaskRunner`), but has logic better contained here.