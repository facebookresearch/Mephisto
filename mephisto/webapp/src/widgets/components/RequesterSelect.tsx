/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import { Select, ItemRenderer } from "@blueprintjs/select";
import { Button, MenuItem } from "@blueprintjs/core";
import { Requester } from "../../models";

type IRequester = Requester;

const RequesterSelect = Select.ofType<IRequester>();

const renderRequesterItem: ItemRenderer<IRequester> = (
  requester,
  { handleClick, modifiers, query }
) => {
  if (!modifiers.matchesPredicate) {
    return null;
  }
  const text = `${requester.requester_id}. ${requester.requester_name}`;
  return (
    <MenuItem
      active={modifiers.active}
      disabled={modifiers.disabled}
      key={requester.requester_id}
      onClick={handleClick}
      text={highlightText(text, query)}
    />
  );
};

export default function RequesterSelectComponent<T>({
  data,
  onUpdate,
}: {
  data: IRequester[];
  onUpdate: Function;
}) {
  const [selected, setSelected] = React.useState<IRequester | null>(null);
  return (
    <div>
      <RequesterSelect
        items={data}
        itemRenderer={renderRequesterItem}
        onItemSelect={(requester: IRequester) => {
          onUpdate({ requester: requester.requester_name });
          setSelected(requester);
        }}
        activeItem={selected}
      >
        <Button icon="map" rightIcon="caret-down">
          {selected ? selected.requester_name : "Pick a requester..."}
        </Button>
      </RequesterSelect>
    </div>
  );
}

function escapeRegExpChars(text: string) {
  return text.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function highlightText(text: string, query: string) {
  let lastIndex = 0;
  const words = query
    .split(/\s+/)
    .filter((word) => word.length > 0)
    .map(escapeRegExpChars);
  if (words.length === 0) {
    return [text];
  }
  const regexp = new RegExp(words.join("|"), "gi");
  const tokens: React.ReactNode[] = [];
  while (true) {
    const match = regexp.exec(text);
    if (!match) {
      break;
    }
    const length = match[0].length;
    const before = text.slice(lastIndex, regexp.lastIndex - length);
    if (before.length > 0) {
      tokens.push(before);
    }
    lastIndex = regexp.lastIndex;
    tokens.push(<strong key={lastIndex}>{match[0]}</strong>);
  }
  const rest = text.slice(lastIndex);
  if (rest.length > 0) {
    tokens.push(rest);
  }
  return tokens;
}
