/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import { Select, ItemRenderer } from "@blueprintjs/select";
import { Button, MenuItem } from "@blueprintjs/core";
import { createAsync } from "../../lib/Async";
import useAxios from "axios-hooks";
import FormField from "./FormField";
import OptionsForm from "./OptionsForm";

type IBlueprint = {
  name: string;
  rank: number;
};

type BlueprintParams = any;

const BlueprintSelect = Select.ofType<IBlueprint>();
const BlueprintParamsAsync = createAsync<BlueprintParams>();

const renderBlueprintItem: ItemRenderer<IBlueprint> = (
  blueprint,
  { handleClick, modifiers, query }
) => {
  if (!modifiers.matchesPredicate) {
    return null;
  }
  const text = `${blueprint.rank}. ${blueprint.name}`;
  return (
    <MenuItem
      active={modifiers.active}
      disabled={modifiers.disabled}
      key={blueprint.rank}
      onClick={handleClick}
      text={highlightText(text, query)}
    />
  );
};

export default function BlueprintSelectComponent<T>({
  data,
  onUpdate,
}: {
  data: IBlueprint[];
  onUpdate: Function;
}) {
  const [selected, setSelected] = React.useState<IBlueprint | null>(null);
  const paramsInfo = useAxios({
    url: `blueprint/${selected?.name || "none"}/options`,
  });

  return (
    <div>
      <BlueprintSelect
        items={data}
        itemRenderer={renderBlueprintItem}
        onItemSelect={(blueprint: IBlueprint) => {
          onUpdate({ blueprint: blueprint.name });
          setSelected(blueprint);
        }}
        activeItem={selected}
      >
        <Button icon="map" rightIcon="caret-down">
          {selected ? selected.name : "Pick a blueprint..."}
        </Button>
      </BlueprintSelect>
      {selected && (
        <BlueprintParamsAsync
          info={paramsInfo}
          onLoading={() => <span>Loading...</span>}
          onError={() => <span>Error</span>}
          onData={({ data }) => (
            <OptionsForm
              onUpdate={onUpdate}
              options={data.options}
              prefix="bp"
            />
          )}
        />
      )}
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
