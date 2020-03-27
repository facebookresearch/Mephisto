# What is this task?
This task exists to demonstrate both the out-of-the-box functionality of setting up a ParlAI chat on Mephisto, as well as more complicated task with custom frontend functionality. 

As of now, to see the two, you have to directly edit the flags at the top of the `parlai_test_script.py` file. 

`USE_LOCAL` determines whether or not the script is launched to `mturk_sandbox` using herokou as a backend (when `False`), or deployed locally for testing (when `True`).

`DEMO_CUSTOM_BUNDLE` determines whether or not to show advanced functionality or just the baseline. `False` will launch the world present in `demo_worlds.py` without any extra functionality, in that it only displays the default chat style, task instructions, etc. `True` will instead load the frontend build stored in `source/build/bundle.js`. If you don't have such a file, or have made changes to `source/dev/components` that you want to see, you'll need to run `npm install; npm run dev` from inside the `source` directory.

# How can I make my own task?
If you have no need for custom frontend functionality, you can use the type of controllability available when `DEMO_CUSTOM_BUNDLE` is `False` by copying over the `demo_worlds.py`, `parlai_test_script.py`, and `task_description.html` files to a new directory (we suggest mephisto/tasks if you don't have a better place, but you can commit these in your own project's directory as well). 

If you do require frontend customization, you should copy the entire contents of this directory, and then make changes to the components you would like to change directly (generally in `source/dev/components/core_components.jsx`). We recommend using [React Dev Tools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi?hl=en) to inspect the specific elements you want to change and debug your frontend as you work with it. Note that after rebuilding your frontend (by using `npm install; npm run dev`) you may need to do a force refresh (shift-cmd-R in chrome) to ensure you load the new version of your bundle.