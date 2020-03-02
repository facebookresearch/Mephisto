import React from "react";
import { Formik } from "formik";
import { InputGroup, FormGroup, Button } from "@blueprintjs/core";
import useAxios from "axios-hooks";
import { createAsync } from "../../lib/Async";
import RequesterTypeSelect from "./RequesterTypeSelect";

type RequesterType = any;
type RequesterTypeParams = any;

const RequesterTypeParamsAsync = createAsync<RequesterTypeParams>();

function RequesterForm() {
  const requesterTypes = ["mturk"];

  const [selectedRequesterType, setSelectedRequesterType] = React.useState<
    string | null
  >(null);

  const requesterTypesAsync = useAxios<RequesterType>({
    url: `/requester/${selectedRequesterType}/options`
  });

  return (
    <div style={{ margin: "40px 0 20px" }}>
      <h3 className="bp3-heading">Add a New Requester:</h3>

      <RequesterTypeSelect
        data={requesterTypes}
        onUpdate={(requesterType: string) => {
          console.log({ requesterType });
          setSelectedRequesterType(requesterType);
        }}
      />
      {selectedRequesterType && (
        <RequesterTypeParamsAsync
          info={requesterTypesAsync}
          onLoading={() => <span>Loading...</span>}
          onError={() => <span>Error</span>}
          onData={({ data: [details] }) => (
            <div style={{ margin: "30px 0 20px" }}>
              <div
                className="bp3-callout bp3-icon-info-sign bp3-intent-primary"
                style={{ margin: "10px 0 30px" }}
              >
                <h4 className="bp3-heading">Details</h4>

                <p className="bp3-text bp3-running-text">{details.desc}</p>
              </div>
              <Formik
                initialValues={{}}
                onSubmit={values => {
                  console.log(values);
                }}
              >
                {({
                  values,
                  errors,
                  touched,
                  handleChange,
                  handleBlur,
                  handleSubmit,
                  isSubmitting
                }) => (
                  <div>
                    {/* {JSON.stringify(details.args)} */}
                    {Object.entries(details.args).map(
                      ([param, details]: [any, any]) => {
                        return (
                          <FormGroup
                            key={param}
                            label={details.help}
                            labelInfo={details.option_string}
                            labelFor="test"
                          >
                            <InputGroup
                              id="requester"
                              placeholder={""}
                              name={param}
                              onBlur={handleBlur}
                              value={(values as any)[param] || ""}
                              onChange={handleChange}
                            ></InputGroup>
                          </FormGroup>
                        );
                      }
                    )}
                    <Button icon="new-person" onClick={() => handleSubmit()}>
                      Add new requester account...
                    </Button>
                  </div>
                )}
              </Formik>
            </div>
          )}
        />
      )}
    </div>
  );
}

export default RequesterForm;
