# Mephisto Toxicity Detection Demo
## Summary

This task presents the worker with a text input.

Written text can only be submitted if its toxicity is is calculated to be <= 0.5. If the toxicity is > 0.5 an alert is shown and the text is not submitted.

The toxicity of written text is calculated from the detoxify python library.

## Steps to run demo

To run the demo first detoxify has to be installed. This can be done using 

```bash
pip install detoxify
```

Then typing 
```bash
python run_task.py
``` 

should run the demo.
