# Simple Static React Task With Tips
This task is essentially the same as the "static-react-task" task except that there is a tips button that allows for the viewing and submission of tips. 

The [static-react-task readme](https://github.com/facebookresearch/Mephisto/blob/add-tips-example/examples/static_react_task/README.md) should be read before running this task.

### Adding Tips
Tips can be imported from `mephisto-worker-addons` to be used.
```js
import { Tips } from "mephisto-worker-addons";
```
Then adding the following to inside your BaseFrontend should show the tips button.
```js
<Tips maxHeight="30rem" maxWidth="35rem" placement="top-start" />
```
To see some of the other props of the Tips component see the 
[mephisto-worker-addons readme](https://github.com/facebookresearch/Mephisto/blob/add-tips-example/packages/mephisto-worker-addons/README.md)

Once a worker submits a tip from the popup that shows when clicking on the tips button, then these tips can be reviewed to either accept or reject them.

This can be done by running the [review_tips_for_task.py](https://github.com/facebookresearch/Mephisto/blob/add-tips-example/mephisto/scripts/local_db/review_tips_for_task.py) script and following the instructions. If a tip is accepted, then running python run_task.py on this task should show the accepted tip when opening the tips popup.

If you accepted a tip by accident, then running the [remove_accepted_tip.py](https://github.com/facebookresearch/Mephisto/blob/add-tips-example/mephisto/scripts/local_db/remove_accepted_tip.py) script and following the instructions will allow you to remove the accepted tip. Running the task again and opening the tips popup will confirm that the accepted tip was removed.

