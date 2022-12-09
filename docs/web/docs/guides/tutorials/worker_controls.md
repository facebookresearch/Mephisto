---
sidebar_position: 3
---

# Introducing worker controls

Now that you have a task to show workers, in order to get quality data you'll want to include a mix of automated and manual reviewing. This guide introduces onboarding, which is a good opportunity to provide workers with a simple test to ensure they read and understand task instructions. A more in-depth guide into their use can be found [here](../../how_to_use/worker_quality/using_onboarding/). We expect familiarity with React's core concepts to understand the frontend part of this tutorial.

**Note:** Generally this flow should be combined with other methods for ensuring quality, such as [screening units](../../how_to_use/worker_quality/using_screen_units/) or [gold units](../../how_to_use/worker_quality/using_golds/).

## 1. Launching with onboarding

Let's extend again from the static react task example, but we'll want to move it to it's own workspace. From within the main Mephisto directory:
```bash
cp -r examples/static_react_task/ tmp/onboarding_tutorial/
cd tmp/onboarding_tutorial/
```

The key for using onboarding is the `onboarding_qualification`, as we can see in `onboarding_example.yaml`:
```yaml
# hydra_configs/conf/onboarding_example.yaml
@package _global_
defaults:
  - /mephisto/blueprint: static_react_task
  - /mephisto/architect: local
  - /mephisto/provider: mock
mephisto:
  blueprint:
    ...
    onboarding_qualification: test-react-static-qualification # This is the key!
  task:
    ...
    task_name: onboarding-tutorial-iterating # Add a custom task name to group the results
```
When Mephisto sees the `mephisto.blueprint.onboarding_qualification` argument, it adds a step to the task that requires workers pass onboarding in order to move on to the main task. Why don't we see it in action? You can launch the onboarding version of this task with `python run_task.py conf=onboarding_example`. Once launched, you can follow through to [`localhost:3000/?worker_id=x&assignment_id=1`](localhost:3000/?worker_id=x&assignment_id=1).

You should be greeted with a panel claiming it is the onboarding task, suggesting that you click a button to move to the main task. Clicking this button puts you into the example static react task. It's not a very informative task as is, so let's add some details into it! Shut down the server and we'll get back to it

## 2. Customizing the onboarding

Onboarding units have three primary components, the initialization data, the view component, and the validation function. Lets change each of these in turn:

### 2.1 Onboarding Initialization Data
In the same way that we used `SharedStaticTaskState.static_task_data` to initialize the `initialTaskData` that is available during a main task, there's a way to initialize that field specifically for onboarding tasks. Let's initialize it with a few test good and bad phrases:

```python
shared_state = SharedStaticTaskState(
    onboarding_data={
        'good': ['Today was good', 'I like ice cream'], 
        'bad': ['Dirt tastes bad', 'Bad news'],
    },
    ...
)
```

Adding the `onboarding_data` field to your `SharedTaskState` is all that needs to be done.

### 2.2 Onboarding View
Now with this data, we can create an onboarding task on the frontend. We'll update the onboarding component to define what we mean by "good text" and "bad text", and then give the worker a few examples to label and submit. 

First let's go to `app.jsx` and pass the task data along to our onboarding component
```js 
// webapp/src/app.jsx
...
  if (isOnboarding) {
    return <OnboardingComponent onboardingData={initialTaskData} onSubmit={handleSubmit} />;
  }
...
```

And now we can go to `core_components.jsx` and put some new components here:
```js
// webapp/src/components/core_components.jsx
// Component for displaying an individual sentence and picking the response
function SentenceDisplay({idx, currSelected, displayText, onChangeSelected}) {
  return (
    <>
      <h3>{displayText}</h3>
      <div className="field is-grouped">
        <div className="control">
          <button
            className="button is-success is-large"
            disabled={currSelected == "good"}
            onClick={() => onChangeSelected({idx, rating: "good" })}
          >
            Mark as Good
          </button>
        </div>
        <div className="control">
          <button
            className="button is-danger is-large"
            disabled={currSelected == "bad"}
            onClick={() => onChangeSelected({idx, rating: "bad" })}
          >
            Mark as Bad
          </button>
        </div>
      </div>
    <br/>
    </>
  );
}

// Replace the existing OnboardingComponent with this one
function OnboardingComponent({ onboardingData, onSubmit }) {
  // Grab the list of good and bad phrases and shuffle them
  const [textList, _setTextList] = React.useState(
    [...onboardingData['good'], ...onboardingData['bad']]
      .map(text => ({ text, rand: Math.random() }))
      .sort((a, b) => a.rand - b.rand)
      .map(({ text }) => text)
  );
  // Create a ratings object to hold the annotations
  const [ratings, updateRatings] = React.useReducer(
    (oldRatings, {idx, rating}) => {
      return oldRatings.map((oldRating, i) =>
        i == idx ? rating : oldRating
      );
    },
    (textList.map(() => null))
  );
  // Function to zip the text list to the ratings
  function zipResults() {
    return Object.fromEntries(textList.map((t, idx) => [t, ratings[idx]]));
  }
  return (
    <div>
      <Directions>
        In this task you'll be presented with a sentence, and need to provide a rating of either "Good" or "Bad". For our definition, all sentences are "good" by default, unless they contain the word "bad". Complete the following 4 examples.
      </Directions>
      <div className="container">
        {
          // Construct an input for each question
          textList.map((text, idx) => <SentenceDisplay
            key={'sentence-'+idx}
            idx={idx}
            displayText={text}
            currSelected={ratings[idx]}
            onChangeSelected={updateRatings}
          />)
        }
      <button
        className="button is-link"
        disabled={ratings.some((val) => val === null)}
        onClick={() => onSubmit({ ratings: zipResults()})}
      >
        Submit Answers
      </button>
      </div>
    </div>
  );
}
```
With this, let's launch again with `python run_task.py conf=onboarding_example`. Once launched, you can follow through to [`localhost:3000/?worker_id=y&assignment_id=1`](localhost:3000/?worker_id=y&assignment_id=1). **Note** that now we're accessing as worker `y`. We do this because worker `x` has already completed onboarding for our task name, and so they'd skip it! Onboarding is only surfaced the _first time_ a worker completes a task by a given `onboarding_qualification`.

![](/tutorial_onboarding_new_interface.png)

This is much more relevant to the core task! Now that we can collect an onboarding, let's move on to validating the content to ensure workers understood the task.

### 2.3 Onboarding validation

The crux of onboarding validation occurs in the function we provide to `validate_onboarding`. In this case, it was:
```python
    def onboarding_always_valid(onboarding_data):
        return True
```
Well, this isn't going to be doing any validation just yet. We'll have to write a new validation function. To do this, let's see what we would have received from `onboarding_data`:
```python
{
  'inputs': {
    'good': ['Today was good', 'I like ice cream'], 
    'bad': ['Dirt tastes bad', 'Bad news']
  },
  'outputs': {
    'ratings': {
      'Dirt tastes bad': 'good', 
      'Today was good': 'good', 
      'I like ice cream': 'bad', 
      'Bad news': 'bad'
    }
  }, 
  'times': {'task_start': 1646947187.8276632, 'task_end': 1646947350.760277}
}
```
From here we can check the inputs and outputs to generate a new onboarding test:
```python
def onboarding_labeled_correctly(onboarding_data):
    for text, rating in onboarding_data['outputs']['ratings'].items():
        if text not in onboarding_data['inputs'][rating]:
            return False
    return True

...

shared_state = SharedStaticTaskState(
  ...
  validate_onboarding=onboarding_labeled_correctly,
)
```

And that's it! Let's move forward to test that this works.

### 2.4 Testing

Let's launch again with `python run_task.py conf=onboarding_example`. Once launched, we should open a tab for [`worker a`](localhost:3000/?worker_id=a&assignment_id=1) and [`worker b`](localhost:3000/?worker_id=b&assignment_id=1). Complete the onboarding correctly as one worker, and assert that you're able to make it through to the task! Complete it incorrectly as the other, and note that you are not qualified to work on the task. With this, you have a functioning basic onboarding task!

## 3. Reviews with onboarding

Mephisto doesn't currently provide out-of-the-box tooling for manually reviewing onboarding tasks, as these should be handled by your own tools. It is certainly possible to query these agents directly to see them though, as you may want to examine what workers are putting in during your onboarding

```python
from mephisto.abstractions.databases.local_database import LocalMephistoDB
db = LocalMephistoDB()
task = db.find_tasks(task_name='onboarding-tutorial-iterating')[0]
onboarding_agents = db.find_onboarding_agents(task_id=task.db_id)
print(onboarding_agents[-1].state.get_data())
# {'inputs': {'good': ['Today was good', 'I like ice cream'], 'bad': ['Dirt tastes bad', 'Bad news']}, 'outputs': {'ratings': {'Today was good': 'good', 'I like ice cream': 'good', 'Bad news': 'bad', 'Dirt tastes bad': 'bad'}}, 'times': {'task_start': 1646948706.989197, 'task_end': 1646948712.4583411}}
```

Retrieving the onboarding unit associated with a specific task unit isn't yet supported, see [#600](https://github.com/facebookresearch/Mephisto/issues/600) if you're interested in potentially helping build this!