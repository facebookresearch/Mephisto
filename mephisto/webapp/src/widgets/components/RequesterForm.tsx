/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from "react";
import { Formik } from "formik";
import { InputGroup, FormGroup, Button } from "@blueprintjs/core";
import useAxios from "axios-hooks";
import { createAsync } from "../../lib/Async";
import ProviderSelect from "./ProviderSelect";
import { createRequester } from "../../service";
import { ParamDetails, LaunchOptions } from "../../models";

type Provider = any;
type ProviderParams = any;

const ProviderParamsAsync = createAsync<ProviderParams>();
const LaunchOptionsAsync = createAsync<LaunchOptions>();

function RequesterForm({
  data,
  onFinish,
}: {
  data: LaunchOptions;
  onFinish: Function;
}) {
  const requesterTypes = data.provider_types;

  const [selectedProvider, setSelectedProvider] = React.useState<string | null>(
    null
  );

  const requesterTypesAsync = useAxios<Provider>({
    url: `/requester/${selectedProvider}/options`,
  });

  return (
    <div style={{ margin: "40px 0 20px" }}>
      <h3 className="bp3-heading">Add a New Requester:</h3>

      <ProviderSelect
        data={requesterTypes}
        onUpdate={(requesterType: string) => {
          console.log({ requesterType });
          setSelectedProvider(requesterType);
        }}
      />
      {selectedProvider && (
        <ProviderParamsAsync
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
                onSubmit={(values: Record<string, string>) => {
                  const results = Object.fromEntries(
                    Object.entries<ParamDetails>(details.args).map(
                      ([param, paramDetails]) => {
                        return [
                          param,
                          {
                            option_string: paramDetails.option_string,
                            value: values[param],
                          },
                        ];
                      }
                    )
                  );
                  createRequester(selectedProvider, results).then(() => {
                    onFinish();
                  });
                }}
              >
                {({
                  values,
                  errors,
                  touched,
                  handleChange,
                  handleBlur,
                  handleSubmit,
                  isSubmitting,
                }) => (
                  <div>
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

function RequesterFormWithData({ onFinish }: { onFinish: Function }) {
  const allRequestersAsync = useAxios<Provider>({
    url: `/launch/options`,
  });

  return (
    <LaunchOptionsAsync
      info={allRequestersAsync}
      onLoading={() => <span>Loading...</span>}
      onError={() => <span>Error</span>}
      onData={({ data }) => <RequesterForm onFinish={onFinish} data={data} />}
    />
  );
}

export default RequesterFormWithData;
