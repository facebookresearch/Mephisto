export function pluralize(num: Number, word: string, plural?: string): string {
  if (num === 1) {
    return word;
  } else return plural || word + "s";
}
