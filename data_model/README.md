# Data Model
## Philosophy
The mephisto data model consists of important classes to formalize some of the concepts that are required for interacting with tasks, crowdsourcing providers, workers, etc. These classes try to abstract away some of the underlying convenience of working with mephisto into a common location, and are designed both to be extended from (in the form of creating child classes for specialized cases, or for the purpose of testing) and behind (like making all of the primary data model components database backed, and eventually supporting a common database for organizational use).
## Classes
TODO expand all of these as they are created.
### Project
High level project that many crowdsourcing tasks may be related to. Useful for budgeting and grouping tasks for a review perspective.
### Task
This class contains all of the required tidbits for launching a set of assignments, including where to find the frontend files to deploy, possible arguments for configuring the assignments more exactly,
### TaskRun
This class keeps track of the configuration options and all assignments associated with an individual launch of a task.
### Assignment
This class represents a single unit of work, or a thing that needs to be done. This can be something like "annotate this specific image" or "Have a conversation between two specified characters." It can be seen as an individual instantiation of the more general `Task` described above.
### SubAssignment
This class represents the role that an individual fills in completing an assignment. An individual worker should only complete one SubAssignment per assignment, which covers the idea of having multiple people in a conversation, or different annotators for a specific task.
### Worker
This class represents an individual - namely a person. It maintains components of ongoing identity for a user.
### Agent
This class encompasses a worker as they are working on an individual assignment. It maintains details for the current task at hand such as start and end time, connection status, etc.

