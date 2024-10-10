/*
 * Copyright (c) Meta Platforms and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

declare type TabType = {
  name: string;
  title: string;
  hoverText?: string;
  hoverTextDisabled?: string;
  children?: React.ReactNode | string;
  noMargins?: boolean;
  disabled?: boolean;
};
