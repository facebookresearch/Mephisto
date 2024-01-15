import fieldIsRequired from "./validators/fieldIsRequired";
import maxLengthSatisfied from "./validators/maxLengthSatisfied";
import minLengthSatisfied from "./validators/minLengthSatisfied";
import regexpSatisfied from "./validators/regexpSatisfied";

// Available name of validator for users in JSON-config -> validator-function
export const validatorFunctionsByConfigName = {
  "maxLength": maxLengthSatisfied,
  "minLength": minLengthSatisfied,
  "required": fieldIsRequired,
  "regexp": regexpSatisfied,
};
