import React from "react";
import { Select, ItemRenderer } from "@blueprintjs/select";
import { Button, MenuItem } from "@blueprintjs/core";
import { RequesterType } from "../../models";

type IRequesterType = RequesterType;

const RequesterTypeSelect = Select.ofType<IRequesterType>();

const renderRequesterTypeItem: ItemRenderer<IRequesterType> = (
  requesterType,
  { handleClick, modifiers, query }
) => {
  if (!modifiers.matchesPredicate) {
    return null;
  }
  const text = `${requesterType}`;
  return (
    <MenuItem
      active={modifiers.active}
      disabled={modifiers.disabled}
      key={requesterType}
      onClick={handleClick}
      text={highlightText(text, query)}
    />
  );
};

export default function RequesterTypeSelectComponent<T>({
  data,
  onUpdate
}: {
  data: IRequesterType[];
  onUpdate: Function;
}) {
  const [selected, setSelected] = React.useState<IRequesterType | null>(null);
  return (
    <div>
      <RequesterTypeSelect
        items={data}
        itemRenderer={renderRequesterTypeItem}
        onItemSelect={(requesterType: IRequesterType) => {
          onUpdate({ requesterType: requesterType });
          setSelected(requesterType);
        }}
        activeItem={selected}
      >
        <Button icon="map" rightIcon="caret-down">
          {selected ? selected : "Pick a requester type..."}
        </Button>
      </RequesterTypeSelect>
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
    .filter(word => word.length > 0)
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
