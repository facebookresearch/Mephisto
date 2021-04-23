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
const SERVER_START_DELAY = TEST_CONSTANTS["ALL"].SERVER_START_DELAY;
const SERVER_STOP_DELAY = TEST_CONSTANTS["ALL"].SERVER_STOP_DELAY;
const BASE_URL = TEST_CONSTANTS["ALL"].BASE_URL;

//for each test type
describe.each([
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
])("Testing if ItemView has all major UI elements", (CONSTANT_KEY) => {
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

  //tests if app can navigate to each item view for every data point given to the server and whether the item view has the correct data
  test(`with: ${CONSTANT_KEY}`, async () => {
    //if data was given to the review server as a file, get data as an array of strings for the specific test type
    const data = TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS
      ? await fileAsArray(
          TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS[1][0],
          TEST_CONSTANTS[CONSTANT_KEY].TYPE
        )
      : null;
    //get the number of pages of data and number of data points per page for specific test type
    const dataPages = TEST_CONSTANTS[CONSTANT_KEY].DATA_PAGE_COUNT;
    const itemsPerPage = TEST_CONSTANTS[CONSTANT_KEY].ITEMS_PER_PAGE;

    //if no data was given to server via file, skip test
    if (!data) return;

    //make new puppeteer instance
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    try {
      //go to root URL of review app
      await page.goto(BASE_URL);

      //get length of review data
      let data_len = data && data.length;
      //for each data point
      let multiplePages = dataPages > 1;
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
        //find item view in allItemView corresponding to specific data point
        await page.waitForSelector(`#item-view-${index}`);
        //go to single itemView
        await page.$eval(`#item-view-${index}`, (div) => div.click());
        await delay(200);
        //make sure app navigated to correct data point
        expect(page.url()).toEqual(`${BASE_URL}${index}`);
        //get data presented on itemView
        const itemView = await page.waitForSelector(`#item-view-${index}`);
        expect(itemView).toBeDefined();
        const textContent = await page.$eval(
          `#item-view-${index}`,
          (itemView) => itemView.textContent
        );
        //match itemView content to the provided content from the file as well as the unique ID identifier for data point (0 indexed position in file)
        const expectedJSON = JSON.parse(data[index]);
        const receivedJSON = JSON.parse(textContent.split("ID: ")[0]);
        expect(receivedJSON).toEqual(expectedJSON);
        expect(textContent).toContain(`ID: ${index}`);
        //make sure all expected buttons are present on itemView
        const approveButton = await page.$eval(
          "#approve-button",
          (button) => !button.disabled
        );
        const rejectButton = await page.$eval(
          "#reject-button",
          (button) => !button.disabled
        );
        const homeButton = await page.$eval(
          "#home-button",
          (button) => !button.disabled
        );
        expect(approveButton).toBeTruthy();
        expect(rejectButton).toBeTruthy();
        expect(homeButton).toBeTruthy();
        //go back to allItemView for next data point
        await page.$eval("#home-button", (button) => button.click());
        await delay(200);
        //make sure we are on all item view
        expect(page.url()).toEqual(BASE_URL);
      }
    } finally {
      await browser.close();
    }
  });
});
