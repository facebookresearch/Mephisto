import React, {Fragment} from "react";
import { useForm, Controller, useWatch} from 'react-hook-form';
import {
    Button, Dialog, AppBar, Toolbar, IconButton, Input, RadioGroup, Radio, FormControlLabel
} from '@material-ui/core';
import {Close} from '@material-ui/icons';
import '../css/style.css';
import {Typography} from '@material-ui/core';


const base_highest = Math.random() < 0.5;

const VALIDATE = {
    exists: v => v.length > 0 || 'Please enter a valid sentence.',
    enough_length: v => v.length > 17 || 'Please enter a whole sentence.',
    numbers: v => v.match(/[0-9]/g) === null || 'Scenarios must not include numbers (0-9).',
    money: v => (
        !(v.includes("$") || v.includes("£") || v.includes("€") || v.includes("dollar")) ||
        'Scenarios must not include money symbols or the word "dollar".'
    ),
    violence: v => (
        !(v.includes("kill") || v.includes("rape") || v.includes("punch") || v.includes("steal")
            || v.includes("stole") || v.includes("shoot") || v.includes("poison")) ||
        "Scenarios should not include violent words like kill, rape, punch, steal, shoot, poison, and so on."
    ),
    giveaway: v => (
        (!(v.includes("happy") || v.includes("nice") || v.includes("okay") || v.includes("decent")
                || v.includes("ok") || v.includes("good") || v.includes("great")
                || v.includes("awesome") || v.includes("terrible") || v.includes("bad") ||
                v.includes("horrible") || v.includes("awful")) ||
            "Scenarios must not include giveaway words like happy, nice, okay, decent, good, bad, great," +
            " and terrible.")
    )
}

function OnboardingComponent({ onSubmit, taskData}) {
    const {handleSubmit, control, formState: { errors } } = useForm();
    return <div style={{margin: "10px"}}>
        <DetailedInstructions taskData={taskData}/>
        <DetailedExamples taskData={taskData}/>
        <hr/>
        <Typography variant="h5" component="div" gutterBottom>Qualification questions</Typography>
        <strong>For each question below, answer whether it is a good example of this task.</strong><br/><br/>
        <form onSubmit={handleSubmit(onSubmit)}>
            {taskData.questions.map((question, i) => (
                <section key={i}>
                    <Typography variant="h6">Question {i+1}</Typography>
                    {question.setup.map((question, j) => (
                        <div key={"setup" + j}> <strong>{question["name"]}: </strong> {question["value"]}<br/></div>
                    ))}
                    <strong>Options:</strong><br/>
                    {question.modifications.map((modification, j) => (
                        <div key={"questions" + j}>({(j + 10).toString(36)}) {modification}<br/></div>
                    ))}
                    <strong>Proposed Ranking: </strong>{question.proposed_ranking}<br/>
                    <strong>Options: </strong>
                    <Controller
                        rules={{ required: { value: true, message: 'Please select an option' } }} control={control}
                        name={"question" + i} defaultValue={null}
                        render={({ field }) => (
                            <RadioGroup {...field}>
                                {question.options.map((option, index) => {
                                    return (
                                        <FormControlLabel
                                            key={index} value={option} control={<Radio />} label={option}
                                        />
                                    );
                                })}
                            </RadioGroup>
                        )}
                    />
                    <br/>
                    <p className="error-message"
                       key={"error" + "question" + i}>{errors["question" + i] ? errors["question" + i]["message"] : ""}
                    </p>
                </section>
            ))}
            <Button type="submit" variant={"outlined"}>Submit</Button>
        </form>
    </div>;
}

function LoadingScreen() {
    return <Directions>Loading...</Directions>;
}

function Directions({ children }) {
    return (
        <section className="hero is-light">
            <div className="hero-body">
                <div className="container">
                    {children}
                </div>
            </div>
        </section>
    );
}

function Disclaimer({}) {
    return (
        <Fragment>
            <p><i><small>This research study is being conducted by the Steinhardt Group at UC Berkeley. For questions
                about this study, please contact Dan Hendrycks at hendrycks@berkeley.edu. In this study, we will ask
                you to write short scenarios and rank them. We would like to remind you that participation in our study
                is voluntary and that you can withdraw from the study at any time.
            </small></i></p><br/>
        </Fragment> );
}

function BasicInstructions({taskData}) {
    return (
        <Fragment>
            <Disclaimer/>
            <Typography variant="h5" component="div" gutterBottom>Instructions</Typography>
            <div dangerouslySetInnerHTML={{__html: taskData.instructions + taskData.extra_instructions}}/>
        </Fragment>
    )
}

function DetailedInstructions({taskData}) {
    return (
        <Fragment>
            <Disclaimer/>
            <Typography variant="h5" component="div" gutterBottom>Detailed Instructions</Typography>
            <div dangerouslySetInnerHTML={{__html: taskData.detailed_instructions}}/>
        </Fragment>
    )
}

function DetailedExamples({taskData}) {
    return (
        <Fragment>
            <hr/>
            <Typography variant="h5" component="div" gutterBottom>
                Examples
            </Typography>
            {taskData.examples.map((example, i) => (
                <section key={i}>
                    <Typography variant="h6">Example {i+1}</Typography>
                    {example.setup.map((setup, j) => (
                        <div key={j}><strong>{setup["name"]}: </strong> {setup["value"]}<br/></div>
                    ))}
                    <strong>Options:</strong><br/>
                    {example.modifications.map((modification, j) => (
                        <div key={"examples" + j}>({(j + 10).toString(36)}) {modification}<br/></div>
                    ))}
                    <strong>Answer: </strong>{example.correct_order}<br/>
                    <strong>Explanation: </strong>{example.explanation}<br/><br/>
                </section>
            ))}
        </Fragment>
    );
}

function BaseEntryComponent({instructions, placeholder, name, control, index}) {
    return (
        <section className="base-entry" key={name + "_base_" + index}>
            <p><b>Part {index+1}: </b>{instructions}</p>
            <Controller
                name={name + "_base"}
                control={control}
                defaultValue=""
                rules={{
                    validate: {
                        first_person: v => (name !== "scenario" || v.includes("I") || v.includes("my") || v.includes("me") || v.includes("My")
                            || 'Scenarios must be written in the first person, and include "I," "my", or "me".'),
                        ...VALIDATE
                    }
                }}
                render={({ field }) => (
                    <Input fullWidth {...field} placeholder={placeholder} autoComplete={"off"}/>
                )}
            />
        </section>
    );
}

function ModificationEntryComponent({placeholder, name, base_value, control, index, enabled, errors}) {
    return (
        <section className="base-entry" key={name + "_modification_" + index}>
            <p>{(typeof base_value !== 'undefined' ? "Original " + name + ": " + base_value: "")}</p>
            {enabled ? <Fragment>
                <Controller
                    name={name + "_modification_" + index}
                    control={control}
                    rules={{
                        validate: VALIDATE
                    }}
                    defaultValue=""
                    render={({ field }) => (
                        <Input fullWidth placeholder={placeholder} autoComplete={"off"} {...field}/>
                    )}
                />
                <p className="error-message">{
                    errors[name + "_modification_" + index] ? errors[name + "_modification_" + index]["message"] : ""
                }</p>
            </Fragment>: null}
        </section>
    );
}

function swap(setValue, getValues, input_config, name1, name2) {
    for (let i = 0; i < input_config.length; i++) {
        let key1 = input_config[i].name + "_modification_" + name1;
        let key2 = input_config[i].name + "_modification_" + name2;
        let temp = getValues(key2);
        setValue(key2, getValues(key1));
        setValue(key1, temp);
    }
}

function SwitchButton({setValue, getValues, input_config, name1, name2, enabled, comparator}) {
    return (
        <section className={"switch-section"}>
            <em>{comparator}</em>
            {enabled ?
                <Button
                    className={"arrow-button"} variant={"outlined"}
                    onClick={(e) => (swap(setValue, getValues, input_config, name1, name2))} type={"button"}>
                    Swap
                </Button> : null
            }
        </section>
    )
}



function Frontend({ taskData, onSubmit}) {
    console.log(taskData);
    const {handleSubmit, control, setValue, getValues, formState: { errors } } = useForm();
    const [open, setOpen] = React.useState(false);
    const [inspiration, setInspiration] = React.useState(null);
    const handleClickOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };
    const getInspiration = () => {
        setInspiration(taskData.inspiration.map((inspiration) => (
            inspiration[Math.floor(Math.random() * inspiration.length)]
        )));
    }

    console.log(taskData);

    return (
        <div>
            <Dialog open={open} onClose={handleClose} fullScreen>
                <AppBar sx={{ position: 'relative' }}> <Toolbar>
                    <IconButton edge="start" color="inherit" onClick={handleClose} aria-label="close"><Close /></IconButton>
                </Toolbar> </AppBar>
                <div style={{"margin": "10px"}}>
                    <BasicInstructions taskData={taskData}/>
                    <DetailedExamples taskData={taskData}/>
                </div>
            </Dialog>
            <Directions>
                <Button variant={"outlined"} onClick={handleClickOpen}>Detailed Instructions & Examples</Button>
                <BasicInstructions taskData={taskData}/>
            </Directions>
            <section className="section"> <div className="container"> <form onSubmit={handleSubmit(onSubmit)}>
                {taskData.input_config.map((thisData, i) => (
                    thisData.base_enabled ?
                        <Fragment key={i}>
                            <BaseEntryComponent
                                instructions={thisData.base_instructions} placeholder={thisData.base_placeholder}
                                name={thisData.name} control={control} index={i}
                            />
                            <p
                                className="error-message" key={"error" + i}>{errors[thisData.name + "_base"] ?
                                errors[thisData.name + "_base"]["message"]: ""}
                            </p>
                            <hr/>
                        </Fragment>: null
                ))}
                <p><b>Part {taskData.input_config.length + 1}: </b>{taskData.modification_instructions}</p>
                {[...Array(taskData.num_inputs)].map((e, i) => (
                    <Fragment key={i}>
                        {i !== 0 ?
                            <SwitchButton
                                setValue={setValue} getValues={getValues} input_config={taskData.input_config}
                                name1={i-1} name2={i}
                                enabled={base_highest && i!==1 || !base_highest && i!==taskData.num_inputs-1}
                                comparator={taskData.comparator}
                            />: null
                        }
                        <section className={"modification-entry"} key={i}>
                            <strong>Full Scenario {i+1}</strong>
                            {taskData.input_config.map((thisData, j) => (
                                <ModificationEntryComponent
                                    key={j} index={i} placeholder={thisData.modification_placeholder}
                                    name={thisData.name}
                                    base_value={useWatch({control, name: thisData.name + "_base"})}
                                    control={control}
                                    enabled={
                                        (base_highest && i!==0 || !base_highest && i!==taskData.num_inputs-1) &&
                                        thisData.modification_enabled
                                    }
                                    errors={errors}
                                />
                            ))}
                        </section>
                    </Fragment>
                ))}
                <div style={{marginBottom: "40px"}}>
                    <Button type={"button"} variant={"outlined"} className={"arrow-button"} onClick={getInspiration}>
                        Get inspiration
                    </Button>
                    <Button type="submit" variant={"outlined"}>Submit</Button>
                </div>
                <div style={{"float": "right", textAlign: "right"}}>
                    {inspiration ? inspiration.map((entry, i) => <p key={i}>{entry}</p>) : null}
                </div>
            </form></div></section>
        </div>
    );
}
export { LoadingScreen, Frontend as BaseFrontend, OnboardingComponent };
