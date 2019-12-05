# mturk-utils

`mturk-utils` makes developing ExternalQuestion tasks for Amazon's mechanical Turk platform easier.

### Philosophy
We consider that a task can be displayed in three different contexts:
1. **Preview mode** - This is when a worker clicks to preview the task before accepting it.
2. **Live mode** - This is when a worker accepts a task and is responsible for completing it.
3. **Review mode** (optional) - This is when a task is being reviewed by an evaluator as part of a post-submission approval process. This is not an officially specified mode by the mTurk platform, however we see it being useful enough in practice that we have first-class support for this use-case.

`mturk-utils` uses mTurk's url conventions to automatically determine for you which state the task is being viewed in. Since "Review mode" is not an officially specified mode by mTurk, we use an arbitrary URL param of `REVIEW_WITH_DATA` to instruct `mturk-utils` to invoke this mode with optional initialization data for the task.

### Install

```bash
yarn add mturk-utils
# or
npm install --save mturk-utils
```

### API

**`getMturkTaskInfo()`**

Returns: An object with properties -
- `isPreview` - `boolean` Is the task being view in Preview mode? You can take action based on this flag such as disabling the Submit button and showing clear instructions.
- `isReview` - `boolean` Is the task being viewed in Review mode? This means that the URL parameter `REVIEW_WITH_DATA` is set. If set, you can use the `deserializeURI` method (also in this library) to parse the parameter's value - which should be a URI encoded JSON payload - and render something that can help an evaluator judge the worker's effort.
- `isLive` - `boolean` Has the task been accepted and is ready for a worker to put effort into?
- `mTurk` - `object` These are the mTurk specific parameters that your app was invoked with. This object contains the following properties, all of type `string`:
    - `assignmentId`
    - `hitId`
    - `turkSubmitTo` - We prefix the mTurk provided hostname with `"/mturk/externalSubmit"` so you do not have to and can directly use this property to submit to.
    - `workerId`
- `params` - `object` Aside from the parameters that mTurk adds to the URL when rendering your ExternalQuestion in an iframe, you can also provide parameters to alter the behavior of your app. Any additional parameters not part of the mTurk specification can be found here.
- `reviewData` - `string` Only set if the task is in Review mode, i.e. `isReview === true`. This is set to whatever was the value of the `REVIEW_WITH_DATA` URL parameter.

#### Other Helper Methods

`serialize(data, encodeURI=false)` - Returns `string`. Take a JSON payload and serialize it to a string. This is useful as a final step when submitting a state object from the task. You can set `encodeURI` to `true` to generate a URL-friendly representation for the string. This needs to be used when passing the data back in through `REVIEW_WITH_DATA` URL param in Review mode.

`deserialize(string_data, encodeURI=false)` Returns `object`. Take a string and deserialize it into a JSON object. This is useful as an initial step when a task is in Review mode. You can then use this object to display a view that an evaluator can find useful. If getting the string data from the URL, you may want to set `encodeURI` to `true`.

`serializeURI(data)` - The same as calling `serialize` but with `encodeURI` set to `true`.

`deserializeURIdata)` - The same as calling `deserialize` but with `encodeURI` set to `true`.