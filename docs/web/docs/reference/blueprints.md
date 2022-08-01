



# Blueprints


The blueprints contain all of the related code required to set up a task run.
## parlai chat


Tasks launched from ParlAI blueprints require the number of
                conversations (either an int or task data for each convo), as
                well as a world to initialize for connecting workers.  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|block_qualification|str|???|Specify the name of a qualification used to soft block workers.|None|False|
|tips_location|str|path_to_task/assets/tips.csv|Path to csv file containing tips|None|False|
|onboarding_qualification|str|???|Specify the name of a qualification used to block workers who fail onboarding, Empty will skip onboarding.|None|False|
|world_file|str|???|Path to file containing ParlAI world|None|True|
|preview_source|str|???|Optional path to source HTML file to preview the task|None|False|
|task_description_file|str|???|Path to file for the extended description of the task. Required if not providing a custom source bundle.|None|False|
|custom_source_bundle|str|???|Optional path to a fully custom frontend bundle|None|False|
|custom_source_dir|str|???|Optional path to a directory containing custom js code|None|False|
|extra_source_dir|str|???|Optional path to sources that the frontend may refer to (such as images/video/css/scripts)|None|False|
|context_csv|str|???|Optional path to csv containing task context|None|False|
|context_jsonl|str|???|Optional path to jsonl file containing task context|None|False|
|num_conversations|int|???|Optional count of conversations to have if no context provided|None|False|

## mock


  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|passed_qualification_name|str|???|Specify the name of a qualification used to designate workers who have passed screening.|None|False|
|max_screening_units|int|???|The maximum number of screening units that can be launched with this batch, specified to limit the number of validations you may need to pay out for.|None|False|
|use_screening_task|bool|False|Whether or not to use a screening task in this run.|None|False|
|onboarding_qualification|str|???|Specify the name of a qualification used to block workers who fail onboarding, Empty will skip onboarding.|None|False|
|block_qualification|str|???|Specify the name of a qualification used to soft block workers.|None|False|
|tips_location|str|path_to_task/assets/tips.csv|Path to csv file containing tips|None|False|
|num_assignments|int|???|How many workers you want to do each assignment|None|True|
|use_onboarding|bool|False|Whether onboarding should be required|None|False|
|timeout_time|int|0|Whether acts in the run assignment should have a timeout|None|False|
|is_concurrent|bool|True|Whether to run this mock task as a concurrent task or not|None|False|

## static task


Tasks launched from static blueprints need a source html file to display to workers, as well as a csv containing values that will be inserted into templates in the html.  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|block_qualification|str|???|Specify the name of a qualification used to soft block workers.|None|False|
|tips_location|str|path_to_task/assets/tips.csv|Path to csv file containing tips|None|False|
|onboarding_qualification|str|???|Specify the name of a qualification used to block workers who fail onboarding, Empty will skip onboarding.|None|False|
|units_per_assignment|int|1|How many workers you want to do each assignment|None|False|
|extra_source_dir|str|???|Optional path to sources that the HTML may refer to (such as images/video/css/scripts)|None|False|
|data_json|str|???|Path to JSON file containing task data|None|False|
|data_jsonl|str|???|Path to JSON-L file containing task data|None|False|
|data_csv|str|???|Path to csv file containing task data|None|False|
|task_source|str|???|Path to source HTML file for the task being run|None|True|
|preview_source|unknown|???|Optional path to source HTML file to preview the task|None|False|
|onboarding_source|unknown|???|Optional path to source HTML file to onboarding the task|None|False|

## remote procedure


Tasks launched from remote query blueprints need a
                source html file to display to workers, as well as a csv
                containing values that will be inserted into templates in
                the html.  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|block_qualification|str|???|Specify the name of a qualification used to soft block workers.|None|False|
|tips_location|str|path_to_task/assets/tips.csv|Path to csv file containing tips|None|False|
|onboarding_qualification|str|???|Specify the name of a qualification used to block workers who fail onboarding, Empty will skip onboarding.|None|False|
|task_source|str|???|Path to file containing javascript bundle for the task|None|True|
|link_task_source|bool|False|                Symlinks the task_source file in your development folder to the                one used for the server. Useful for local development so you can run                a watch-based build for your task_source, allowing the UI code to                update without having to restart the server each time.            |None|False|
|units_per_assignment|int|1|How many workers you want to do each assignment|None|False|

## static react task


Tasks launched from static blueprints need
                a prebuilt javascript bundle containing the task. We suggest building
                with our provided useMephistoTask hook.  

|dest|type|default|help|choices|required|
| :--- | :--- | :--- | :--- | :--- | :--- |
|block_qualification|str|???|Specify the name of a qualification used to soft block workers.|None|False|
|tips_location|str|path_to_task/assets/tips.csv|Path to csv file containing tips|None|False|
|onboarding_qualification|str|???|Specify the name of a qualification used to block workers who fail onboarding, Empty will skip onboarding.|None|False|
|units_per_assignment|int|1|How many workers you want to do each assignment|None|False|
|extra_source_dir|str|???|Optional path to sources that the HTML may refer to (such as images/video/css/scripts)|None|False|
|data_json|str|???|Path to JSON file containing task data|None|False|
|data_jsonl|str|???|Path to JSON-L file containing task data|None|False|
|data_csv|str|???|Path to csv file containing task data|None|False|
|task_source|str|???|Path to file containing javascript bundle for the task|None|True|
|link_task_source|bool|False|                Symlinks the task_source file in your development folder to the                one used for the server. Useful for local development so you can run                a watch-based build for your task_source, allowing the UI code to                update without having to restart the server each time.            |None|False|
