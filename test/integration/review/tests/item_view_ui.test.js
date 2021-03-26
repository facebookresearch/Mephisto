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

describe.each([
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
])("Testing if ItemView has all major UI elements", (CONSTANT_KEY) => {
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

  test(`with: ${CONSTANT_KEY}`, async () => {
    const data = TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS
      ? await fileAsArray(
          TEST_CONSTANTS[CONSTANT_KEY].DATA_COLLECTION_ARGS[1][0],
          TEST_CONSTANTS[CONSTANT_KEY].TYPE
        )
      : null;
    const dataPages = TEST_CONSTANTS[CONSTANT_KEY].DATA_PAGE_COUNT;
    const itemsPerPage = TEST_CONSTANTS[CONSTANT_KEY].ITEMS_PER_PAGE;

    if (!data) return;

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(BASE_URL);

    try {
      let data_len = data && data.length;
      let multiplePages = dataPages > 1;
      for (var index = 0; index < data_len; index += 1) {
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
        await page.waitForSelector(`#item-view-${index}`);
        await page.$eval(`#item-view-${index}`, (div) => div.click());
        await delay(200);
        expect(page.url()).toEqual(`${BASE_URL}${index}`);
        //await page.screenshot({path:`${CONSTANT_KEY}-review.png`, fullPage:true})
        const itemView = await page.waitForSelector(`#item-view-${index}`);
        expect(itemView).toBeDefined();
        const textContent = await page.$eval(
          `#item-view-${index}`,
          (itemView) => itemView.textContent
        );
        const expectedJSON = JSON.parse(data[index]);
        const receivedJSON = JSON.parse(textContent.split("ID: ")[0]);
        expect(receivedJSON).toEqual(expectedJSON);
        expect(textContent).toContain(`ID: ${index}`);
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
        await page.$eval("#home-button", (button) => button.click());
        await delay(200);
        expect(page.url()).toEqual(BASE_URL);
      }
    } finally {
      await browser.close();
    }
  });
});
