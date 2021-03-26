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

describe.each([
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
])("Testing if AllItemView has all major UI elements", (CONSTANT_KEY) => {
  const server = new Server();

  beforeAll(async () => {
    const started = await server.start(
      TEST_CONSTANTS[CONSTANT_KEY].SERVER_START_ARGS,
      TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS,
      SERVER_START_DELAY,
      TEST_CONSTANTS[CONSTANT_KEY].DEFAULT_SERVER_OUTPUT
    );

    expect(started).toBeTruthy();
  });

  afterAll(async () => {
    const stopped = await server.stop(SERVER_STOP_DELAY);

    expect(stopped).toBeTruthy();
  });

  test(`when navigating data with: ${CONSTANT_KEY}`, async () => {
    const data = TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS
      ? await fileAsArray(
          TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS[1][0],
          TEST_CONSTANTS[CONSTANT_KEY].TYPE
        )
      : null;
    const dataPages = TEST_CONSTANTS[CONSTANT_KEY].DATA_PAGE_COUNT;

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    try {
      await page.goto(BASE_URL);

      var linksDict = {};
      var pageCount = 0;

      if (dataPages > 1) {
        await page.waitForSelector("#pagination-button-left");
        var isDisabled = await page.$eval(
          "#pagination-button-left",
          (button) => button.disabled
        );
        expect(isDisabled).toBeTruthy();
      }

      while (pageCount < dataPages) {
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
          await page.waitForSelector("#pagination-button-right");
          isDisabled = await page.$eval(
            "#pagination-button-right",
            (button) => button.disabled
          );
          expect(isDisabled).toBeFalsy();
          await page.click("#pagination-button-right");
        } else if (dataPages > 1) {
          await page.waitForSelector("#pagination-button-right");
          isDisabled = await page.$eval(
            "#pagination-button-right",
            (button) => button.disabled
          );
          expect(isDisabled).toBeTruthy();
        }
      }
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

  test(`when searching data with: ${CONSTANT_KEY}`, async () => {
    const searchTestOptions = TEST_CONSTANTS[CONSTANT_KEY].SEARCH_TEST_OPTIONS;

    if (!searchTestOptions) return;

    const resultDataPages = searchTestOptions.RESULT_DATA_PAGE_COUNT;
    const expectedResultCount = searchTestOptions.EXPECTED_RESULT_COUNT;

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    try {
      await page.goto(BASE_URL);
      var searchBar = await page.waitForSelector("#mephisto-search");
      expect(searchBar).toBeDefined();
      await page.type("#mephisto-search", searchTestOptions.QUERY);
      var searchButton = await page.waitForSelector("#mephisto-search-button");
      expect(searchButton).toBeDefined();
      await page.$eval("#mephisto-search-button", (button) => button.click());
      await delay(500);

      var linksDict = {};
      var pageCount = 0;

      while (pageCount < resultDataPages) {
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
        if (pageCount < resultDataPages) {
          await page.waitForSelector("#pagination-button-right");
          await page.click("#pagination-button-right");
        }
      }

      const linksKeys = Object.keys(linksDict);
      expect(linksKeys).toBeDefined();
      const receivedResultCount = linksKeys.length;
      expect(receivedResultCount).toEqual(expectedResultCount);

      for (const href of linksKeys) {
        const textContent = linksDict[href];
        expect(textContent).toContain(searchTestOptions.QUERY);
      }
    } finally {
      await browser.close();
    }
  });
});
