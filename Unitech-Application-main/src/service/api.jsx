import { API } from "aws-amplify";

const API_NAME = "UnitechAWS";

export const fetchData = async ({
  apiName = API_NAME,
  endpoint = "/",
  additionalParams = {},
} = {}) => {
  return await API.get(apiName, endpoint, additionalParams);
};

export const setParameters = (parameters) => ({
  queryStringParameters: parameters,
});

export const postData = async ({
  apiName = API_NAME,
  endpoint = "/",
  body = {},
} = {}) => {
  console.log(body);
  return await API.post(apiName, endpoint, { body: body });
};
