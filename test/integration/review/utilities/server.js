/**
 * Class allows user to start and stop mephisto review server for purpose of tests
 */
import { spawn } from "child_process";
import { delay } from "./test_tools";

export default class Server {
  constructor() {
    this.server = null;
  }

  /**
   * starts mephisto review server with given arguments. Returns true for successful start, false for unsuccessful start
   * @param {Array} server_start_args REQUIRED arguments for a Node.js spawn child process to create a mephisto review server
   * @param {Array} data_collection_args OPTIONAL arguments for a Node.js spawn child process to send standard input of data points to review server
   * @param {Number} delay_in_ms OPTIONAL represents time in milliseconds to wait for review server to start before checking status
   * @param {String} expected_server_output OPTIONAL represents expected standard output from review server upon successful start. Is matched to received output to check status of server
   * @param {Function} stdoutCallBack OPTIONAL function to handle standard output of server after successful start
   */
  async start(
    server_start_args,
    data_collection_args,
    delay_in_ms,
    expected_server_output,
    stdoutCallBack
  ) {
    //if server is already started cannot start server again
    if (this.server != null || server_start_args == null) return false;
    var server_stdout = "";
    var server_err = null;
    const collectsData = data_collection_args != null;
    //if inputting data as stdin to review server, create child process to get data
    if (collectsData) var data_col = await spawn(...data_collection_args);
    //start review server
    this.server = await spawn(...server_start_args);
    //if spawn error, kill data collection process and return false
    if (typeof this.server.pid !== "number") {
      this.server = null;
      if (collectsData) data_col.kill("SIGTERM");
      return false;
    }
    //record any standard errors from server
    this.server.on("error", (err) => {
      server_err = err;
    });
    //if checking for output message from server, attach stdout listener to server
    if (expected_server_output != null)
      this.server.stdout.on("data", (data) => {
        const stdout = data.toString();
        server_stdout += stdout;
      });

    //if no errors and user wants to input data to server, pipe output from data collection process to server input
    if (server_err == null && collectsData)
      data_col.stdout.pipe(this.server.stdin);
    //if delay is used, wait delay for server to start
    if (delay_in_ms) await delay(delay_in_ms);
    //if server error or expected standard output was not received, kill child processes and return false
    if (
      server_err != null ||
      (expected_server_output != null &&
        expected_server_output != server_stdout)
    ) {
      if (collectsData) data_col.kill("SIGTERM");
      await this.server.stdin.write("\x03");
      await this.server.stdin.end();
      await delay(500);
      this.server.kill("SIGTERM");
      await delay(500);
      this.server = null;
      return false;
    }
    //kill data collection process as it is no longer in use
    if (collectsData) data_col.kill("SIGTERM");
    //if stdout handler was given, attach to server
    if (stdoutCallBack) this.server.stdout.on("data", stdoutCallBack);
    //server started successfully
    return true;
  }

  /**
   * stops mephisto review server. Returns true upon successful stop, false upon unsuccessful stop
   * @param {Number} delay_in_ms OPTIONAL represents the time to wait for server to stop after kill command is sent
   */
  async stop(delay_in_ms) {
    //if server doesn't exist, cannot stop it
    if (!this.server) return false;
    //attach an exit handler to record an exit signal from server
    var exited = false;
    this.server.on("exit", (exit) => {
      exited = true;
    });
    //send cancel command to server
    await this.server.stdin.write("\x03");
    await this.server.stdin.end();
    //wait for command to take effect
    await delay(500);
    //kill child process for server
    const killed = await this.server.kill("SIGTERM");
    //wait delay for server to stop if given delay
    if (delay_in_ms) await delay(delay_in_ms);
    //if exit signal was recorded or server has an exit code server was stopped successfully
    if (exited || this.server.exitCode != null) {
      this.server = null;
      return true;
    }
    //unsuccessful stop
    return false;
  }
}
