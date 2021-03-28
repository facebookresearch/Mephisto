import puppeteer from "puppeteer";
import Server from "../utilities/server";
import { fileAsArray } from "../utilities/file_management";
import {
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
} from "./test_types";
import TEST_CONSTANTS from "./test_constants";
import { delay } from "../utilities/test_tools";
const REJECTED_REVIEW = TEST_CONSTANTS["ALL"].REJECTED_REVIEW;
const APPROVED_REVIEW = TEST_CONSTANTS["ALL"].APPROVED_REVIEW;
const BASE_URL = TEST_CONSTANTS["ALL"].BASE_URL;
const SERVER_START_DELAY = TEST_CONSTANTS["ALL"].SERVER_START_DELAY;
const SERVER_STOP_DELAY = TEST_CONSTANTS["ALL"].SERVER_STOP_DELAY;

//for each test type
describe.each([
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
])("Testing if review creates appropriate results file", (CONSTANT_KEY) => {
  const server = new Server();
  //array for recording standard output from an instance of the review server
  var results = [];
  //function to record standard output from review server
  const stdoutHandler = (data) => results.push(data.toString());

  //before all tests, start review server with a callback to record standard output
  //server_start_args must be for a review server that records reviews in standard output
  beforeAll(async () => {
    const started = await server.start(
      TEST_CONSTANTS[CONSTANT_KEY].SERVER_START_ARGS,
      TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS,
      SERVER_START_DELAY,
      TEST_CONSTANTS[CONSTANT_KEY].DEFAULT_SERVER_OUTPUT,
      stdoutHandler
    );

    expect(started).toBeTruthy();
  });

  //after all tests stop review server
  afterAll(async () => {
    const stopped = await server.stop(SERVER_STOP_DELAY);
    expect(stopped).toBeTruthy();
  });

  //tests whether reviewing each data point creates the correct standard output when approving all data points
  test(`when approving all with: ${CONSTANT_KEY}`, async () => {
    //reset standard output array
    results = [];
    //if data was given to review server via file, get all data points as an array of strings
    const data = TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS
      ? await fileAsArray(
          TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS[1][0],
          TEST_CONSTANTS[CONSTANT_KEY].TYPE
        )
      : null;
    //get number of pages of data review app will show in test
    const dataPages = TEST_CONSTANTS[CONSTANT_KEY].DATA_PAGE_COUNT;
    //get number of items each page of data can show
    const itemsPerPage = TEST_CONSTANTS[CONSTANT_KEY].ITEMS_PER_PAGE;

    //if no data was provided to server via file skip test
    if (!data) return;

    //create new instance of puppeteer
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    //get length of data in test as well as whether there are multiple pages of data
    let data_len = data && data.length;
    let multiplePages = dataPages > 1;
    try {
      //go to root URL of review app
      await page.goto(BASE_URL);
      //for each data point
      for (var index = 0; index < data_len; index += 1) {
        //if data point is not on first page navigate to correct page
        if (multiplePages && index != 0 && index % itemsPerPage >= 0) {
          const pagesForward = Math.floor(index / itemsPerPage);
          for (
            var pagesTravelled = 0;
            pagesTravelled < pagesForward;
            pagesTravelled += 1
          ) {
            await page.waitForSelector("#pagination-button-right");
            await page.click("#pagination-button-right");
            await delay(200);
          }
        }
        //approve data point
        await page.waitForSelector(`#item-view-${index}`);
        await page.$eval(`#item-view-${index}`, (div) => div.click());
        await delay(200);
        await page.$eval("#approve-button", (button) => button.click());
        await delay(200);
        //go back to allItemView
        await page.$eval("#home-button", (button) => button.click());
        await delay(200);
        expect(page.url()).toEqual(BASE_URL);
      }
    } finally {
      await browser.close();
    }
    //for each data point, make sure there is standard output for an approved review in the correct order by matching the ID identifier
    for (var index = 0; index < data_len; index += 1) {
      expect(results[index]).toContain(`ID: ${index}`);
      expect(results[index]).toContain(APPROVED_REVIEW);
    }
  });

  //tests whether reviewing each data point creates the correct standard output when rejecting all data points
  test(`when rejecting all with: ${CONSTANT_KEY}`, async () => {
    //reset standard output array
    results = [];
    //if data was given to review server via file, get all data points as an array of strings
    const data = TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS
      ? await fileAsArray(
          TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS[1][0],
          TEST_CONSTANTS[CONSTANT_KEY].TYPE
        )
      : null;
    //get number of pages of data review app will show in test
    const dataPages = TEST_CONSTANTS[CONSTANT_KEY].DATA_PAGE_COUNT;
    //get number of items each page of data can show
    const itemsPerPage = TEST_CONSTANTS[CONSTANT_KEY].ITEMS_PER_PAGE;

    //if no data was provided to server via file skip test
    if (!data) return;

    //create new instance of puppeteer
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    //get length of data in test as well as whether there are multiple pages of data
    let data_len = data && data.length;
    let multiplePages = dataPages > 1;
    try {
      //go to root URL of review app
      await page.goto(BASE_URL);
      //for each data point
      for (var index = 0; index < data_len; index += 1) {
        //if data point is not on first page navigate to correct page
        if (multiplePages && index != 0 && index % itemsPerPage >= 0) {
          const pagesForward = Math.floor(index / itemsPerPage);
          for (
            var pagesTravelled = 0;
            pagesTravelled < pagesForward;
            pagesTravelled += 1
          ) {
            await page.waitForSelector("#pagination-button-right");
            await page.click("#pagination-button-right");
            await delay(200);
          }
        }
        //reject data point
        await page.waitForSelector(`#item-view-${index}`);
        await page.$eval(`#item-view-${index}`, (div) => div.click());
        await delay(200);
        await page.$eval("#reject-button", (button) => button.click());
        await delay(200);
        //go back to allItemView
        await page.$eval("#home-button", (button) => button.click());
        await delay(200);
        expect(page.url()).toEqual(BASE_URL);
      }
    } finally {
      await browser.close();
    }
    //for each data point, make sure there is standard output for an approved review in the correct order by matching the ID identifier
    for (var index = 0; index < data_len; index += 1) {
      expect(results[index]).toContain(`ID: ${index}`);
      expect(results[index]).toContain(REJECTED_REVIEW);
    }
  });
});
