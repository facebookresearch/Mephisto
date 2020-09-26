**NOTE: These instructions are from before Hydra integration. They will need to be upated after Hydra integration**

To run the example in this directory, modify `parlai_test_script.py` in the parent directory replacing:

```
source_dir_path = f"{TASK_DIRECTORY}/custom_simple"
```

with:

```
source_dir_path = f"{TASK_DIRECTORY}/custom_input_and_messages"
```

You can then run the task with:
```
python parlai_test_script.py --build-custom-task True
```

---

### Additional Notes

If you are locally developing on a library package such as `bootstrap-chat`, you might receive an unsymlinked version of the package in the `_generated` folder.

The `_generated` folder is created after each build - which only occurs whenever the source directory is modified.

So to temporarily work around this, run the run script so a `_generated` folder gets created, cancel out, then do:

```
cd custom_input_and_messages/_generated
npm link bootstrap-chat
npm run dev
cd ../..
```

Now when you run the script again, the fixed, symlinked `_generated` from the previous cancelled run will be used.