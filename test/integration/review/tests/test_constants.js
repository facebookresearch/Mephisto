/**
 * Constant properties common to all tests of a given test type, certain attributes are mandatory for functionality of tests
 */

//get all test types
import {
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
} from "./test_types";

//path to python binary used by tests
const PYTHON_PATH = "../../../venv/bin/python3";

export default {
  //MANDATORY for all tests, represents information common to all test types
  ALL: {
    //time to wait for server to start successfully
    SERVER_START_DELAY: 2000,
    //time to wait for server to stop successfully
    SERVER_STOP_DELAY: 1000,
    //root URL of review app
    BASE_URL: "http://127.0.0.1:5000/",
    //result review app will record upon rejecting a review
    REJECTED_REVIEW: "REVIEW: {'result': 'rejected'}",
    //result review app will record upon approving a review
    APPROVED_REVIEW: "REVIEW: {'result': 'approved'}",
  },
  //match test type string identifier to key of test constant attribute
  [CSV_MULTI_PAGE_DATA]: {
    //MANDATORY for all tests, arguments for Nodejs spawn process to start mephisto review server
    SERVER_START_ARGS: [
      PYTHON_PATH,
      [
        "../../../mephisto/client/cli.py",
        "review",
        "test_app/build",
        "--stdout",
        "--all",
      ],
    ],
    //used to create Nodejs spawn process to load standard input of data points into mephisto review server
    DATA_COLLECTION_ARGS: ["cat", ["test_data/CSV/multi_page_data.csv"]],
    //used to check if review server started properly, is supposed to match server output upon successful start
    DEFAULT_SERVER_OUTPUT:
      "Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n",
    //type of data being used to run mephisto review server
    TYPE: "CSV",
    //MANDATORY for item_view_ui and review_results tests amount of pages of data review app will display during test
    DATA_PAGE_COUNT: 2,
    //MANDATORY for item_view_ui and review_results tests number of data points review app will show on each page during test
    ITEMS_PER_PAGE: 9,
    //MANDATORY for search portion of all_item_view_ui test
    SEARCH_TEST_OPTIONS: {
      //MANDATORY, represents the query used on review app search bar
      QUERY: "bad",
      //expected amount of data points to match query
      EXPECTED_RESULT_COUNT: 6,
      //expected number of pages of data points review app will show upon query
      RESULT_DATA_PAGE_COUNT: 1,
    },
  },
  [CSV_SINGLE_PAGE_DATA]: {
    SERVER_START_ARGS: [
      PYTHON_PATH,
      [
        "../../../mephisto/client/cli.py",
        "review",
        "test_app/build",
        "--stdout",
        "--all",
      ],
    ],
    DATA_COLLECTION_ARGS: ["cat", ["test_data/CSV/single_page_data.csv"]],
    DEFAULT_SERVER_OUTPUT:
      "Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n",
    TYPE: "CSV",
    DATA_PAGE_COUNT: 1,
    ITEMS_PER_PAGE: 9,
    SEARCH_TEST_OPTIONS: {
      QUERY: "bad",
      EXPECTED_RESULT_COUNT: 4,
      RESULT_DATA_PAGE_COUNT: 1,
    },
  },
  [JSON_MULTI_PAGE_DATA]: {
    SERVER_START_ARGS: [
      PYTHON_PATH,
      [
        "../../../mephisto/client/cli.py",
        "review",
        "test_app/build",
        "--stdout",
        "--all",
        "--json",
      ],
    ],
    DATA_COLLECTION_ARGS: ["cat", ["test_data/JSON/multi_page_data.jsonl"]],
    DEFAULT_SERVER_OUTPUT:
      "Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n",
    TYPE: "JSON",
    DATA_PAGE_COUNT: 2,
    ITEMS_PER_PAGE: 9,
    SEARCH_TEST_OPTIONS: {
      QUERY: "13",
      EXPECTED_RESULT_COUNT: 6,
      RESULT_DATA_PAGE_COUNT: 1,
    },
  },
  [JSON_SINGLE_PAGE_DATA]: {
    SERVER_START_ARGS: [
      PYTHON_PATH,
      [
        "../../../mephisto/client/cli.py",
        "review",
        "test_app/build",
        "--stdout",
        "--all",
        "--json",
      ],
    ],
    DATA_COLLECTION_ARGS: ["cat", ["test_data/JSON/single_page_data.jsonl"]],
    DEFAULT_SERVER_OUTPUT:
      "Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n",
    TYPE: "JSON",
    DATA_PAGE_COUNT: 1,
    ITEMS_PER_PAGE: 9,
    SEARCH_TEST_OPTIONS: {
      QUERY: "13",
      EXPECTED_RESULT_COUNT: 5,
      RESULT_DATA_PAGE_COUNT: 1,
    },
  },
};
