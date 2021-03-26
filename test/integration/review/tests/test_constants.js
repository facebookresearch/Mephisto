import {
  CSV_MULTI_PAGE_DATA,
  CSV_SINGLE_PAGE_DATA,
  JSON_MULTI_PAGE_DATA,
  JSON_SINGLE_PAGE_DATA,
} from "./test_types";

const PYTHON_PATH = "../../../venv/bin/python3";

export default {
  [CSV_MULTI_PAGE_DATA]: {
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
    DATA_COLLECTION_ARGS: ["cat", ["test_data/CSV/multi_page_data.csv"]],
    DEFAULT_SERVER_OUTPUT:
      "Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n",
    TYPE: "CSV",
    DATA_PAGE_COUNT: 2,
    ITEMS_PER_PAGE: 9,
    SEARCH_TEST_OPTIONS: {
      QUERY: "bad",
      EXPECTED_RESULT_COUNT: 6,
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
  ALL: {
    SERVER_START_DELAY: 1000,
    SERVER_STOP_DELAY: 500,
    BASE_URL: "http://127.0.0.1:5000/",
    REJECTED_REVIEW: "REVIEW: {'result': 'rejected'}",
    APPROVED_REVIEW: "REVIEW: {'result': 'approved'}",
  },
};
