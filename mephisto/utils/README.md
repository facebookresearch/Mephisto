# Utils
Contains classes and utility functions that are generally useful for Mephisto classes to rely on and which don't better belong in a specific subfolder. These are differ from `tools`, which are more likely to be used directly by external Mephisto users rather than internal Mephisto classes.

## `metrics.py`
This file contains useful functionality for managing the prometheus and grafana servers associated with Mephisto.

## `logger_core.py`
This module contains helpers to simplify the process of generating unique loggers and logging configuration for various parts of Mephisto. At the moment this only outlines the basic logging style that Mephisto uses, though much is still to be done in order to set up logging throughout Mephisto, simplified controls for getting debug information across certain files, and user configuration of Mephisto logs.

## `dirs.py`
This file contains number of helper utils that (at the moment) rely on the local-storage implementation of Mephisto. These utils help navigate the files present in the mephisto architecture, identify task files, link classes, etc. Docstrings in this class explain in more detail.

## `testing.py`
This file contains functions that are specifically useful for setting up mock data in tests.

## `qualifications.py`
This file contains helpers that are used for interfacing with or creating Mephisto qualifications.