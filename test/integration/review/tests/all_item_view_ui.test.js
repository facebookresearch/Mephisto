import puppeteer from "puppeteer";
import Server from "../utilities/server";
import { delay } from "../utilities/test_tools";
import { fileAsArray } from "../utilities/file_management";
import {
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
} from "./test_types";
import TEST_CONSTANTS from "./test_constants";
const SERVER_START_DELAY = TEST_CONSTANTS["ALL"].SERVER_START_DELAY;
const SERVER_STOP_DELAY = TEST_CONSTANTS["ALL"].SERVER_STOP_DELAY;
const BASE_URL = TEST_CONSTANTS["ALL"].BASE_URL;

//for each test type
describe.each([
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
])("Testing if AllItemView has all major UI elements", (CONSTANT_KEY) => {
  const server = new Server();

  //before each test start mephisto review server for parameters specific to each test type
  beforeAll(async () => {
    const started = await server.start(
      TEST_CONSTANTS[CONSTANT_KEY].SERVER_START_ARGS,
      TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS,
      SERVER_START_DELAY,
      TEST_CONSTANTS[CONSTANT_KEY].DEFAULT_SERVER_OUTPUT
    );

    expect(started).toBeTruthy();
  });

  //after each test stop mephisto review server
  afterAll(async () => {
    const stopped = await server.stop(SERVER_STOP_DELAY);

    expect(stopped).toBeTruthy();
  });

  //tests the ability for the app to navigate paginated content to view all provided data points on the review app
  test(`when navigating data with: ${CONSTANT_KEY}`, async () => {
    //if test provides file based data as standard input for the mephisto review server, get file contents as an array of strings
    const data = TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS
      ? await fileAsArray(
          TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS[1][0],
          TEST_CONSTANTS[CONSTANT_KEY].TYPE
        )
      : null;
    //record the number of pages of data the review will be expected to show according to the test type
    const dataPages = TEST_CONSTANTS[CONSTANT_KEY].DATA_PAGE_COUNT;

    //launch a new puppeteer instance
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    try {
      //try going to root URL for review app
      await page.goto(BASE_URL);

      //var to record href elements present on the review app
      var linksDict = {};
      //var to count the number of traveresed pages of data in review app
      var pageCount = 0;

      //if app should show multiple pages of data, make sure left pagination button is present and is disabled on the first page
      if (dataPages > 1) {
        await page.waitForSelector("#pagination-button-left");
        var isDisabled = await page.$eval(
          "#pagination-button-left",
          (button) => button.disabled
        );
        expect(isDisabled).toBeTruthy();
      }

      //while all pages of expected data have not been traversed
      while (pageCount < dataPages) {
        //get all href elements from page
        var links = await page.$$eval("a", (links) =>
          links.map((link) => ({
            href: link.href,
            textContent: link.textContent,
          }))
        );
        for (const link of links) {
          linksDict[link.href] = link.textContent;
        }
        pageCount += 1;
        if (pageCount < dataPages) {
          //if not on last page make sure next page button is available and go to next page
          await page.waitForSelector("#pagination-button-right");
          isDisabled = await page.$eval(
            "#pagination-button-right",
            (button) => button.disabled
          );
          expect(isDisabled).toBeFalsy();
          await page.click("#pagination-button-right");
        } else if (dataPages > 1) {
          //if on last page on a paginated review, make sure next page button is disabled
          await page.waitForSelector("#pagination-button-right");
          isDisabled = await page.$eval(
            "#pagination-button-right",
            (button) => button.disabled
          );
          expect(isDisabled).toBeTruthy();
        }
      }
      //if data was inputted via a file
      //for each line of file, make sure the app displayed the correct JSON data and unique ID identifier (0-indexed position of data on file)
      let data_len = data && data.length;
      if (data)
        for (var index = 0; index < data_len; index += 1) {
          const expectedHref = `${BASE_URL}${index}`;
          const textContent = linksDict[expectedHref];
          const expectedJSON = JSON.parse(data[index]);
          const receivedJSON = JSON.parse(textContent.split("ID: ")[0]);
          expect(receivedJSON).toEqual(expectedJSON);
          expect(textContent).toContain(`ID: ${index}`);
        }
    } finally {
      await browser.close();
    }
  });

  //tests the ability to use the search bar to filter data based on search tests specified for each test type
  test(`when searching data with: ${CONSTANT_KEY}`, async () => {
    //get search test for specific test type
    const searchTestOptions = TEST_CONSTANTS[CONSTANT_KEY].SEARCH_TEST_OPTIONS;

    //if no search test skip test
    if (!searchTestOptions) return;

    //expected number of pages of results and expected number of results
    const resultDataPages = searchTestOptions.RESULT_DATA_PAGE_COUNT;
    const expectedResultCount = searchTestOptions.EXPECTED_RESULT_COUNT;

    //launch new instance of puppeteer
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    try {
      //go to root URL of review app
      await page.goto(BASE_URL);
      //make sure search bar and search button exist and search given test query
      var searchBar = await page.waitForSelector("#mephisto-search");
      expect(searchBar).toBeDefined();
      await page.type("#mephisto-search", searchTestOptions.QUERY);
      var searchButton = await page.waitForSelector("#mephisto-search-button");
      expect(searchButton).toBeDefined();
      await page.$eval("#mephisto-search-button", (button) => button.click());
      //wait for server to generate results
      await delay(500);

      //var to record href elements present on the review app
      var linksDict = {};
      //var to count the number of traveresed pages of data in review app
      var pageCount = 0;

      //while there are more pages of results available
      while (pageCount < resultDataPages) {
        //get all href elements from page
        var links = await page.$$eval("a", (links) =>
          links.map((link) => ({
            href: link.href,
            textContent: link.textContent,
          }))
        );
        for (const link of links) {
          linksDict[link.href] = link.textContent;
        }
        pageCount += 1;
        //go to next page
        if (pageCount < resultDataPages) {
          await page.waitForSelector("#pagination-button-right");
          await page.click("#pagination-button-right");
        }
      }

      //check if number of results matches expected number of results
      const linksKeys = Object.keys(linksDict);
      expect(linksKeys).toBeDefined();
      const receivedResultCount = linksKeys.length;
      expect(receivedResultCount).toEqual(expectedResultCount);

      //for each results, make sure search query term exists in stringified JSON data
      for (const href of linksKeys) {
        const textContent = linksDict[href];
        expect(textContent).toContain(searchTestOptions.QUERY);
      }
    } finally {
      await browser.close();
    }
  });
});
