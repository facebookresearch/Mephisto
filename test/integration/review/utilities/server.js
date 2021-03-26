import { spawn } from "child_process";
import { delay } from "./test_tools";

export default class Server {
  constructor() {
    this.server = null;
  }

  async start(
    server_start_args,
    data_collection_args,
    delay_in_ms,
    expected_server_output,
    stdoutCallBack
  ) {
    if (this.server != null || server_start_args == null) return false;
    var server_stdout = "";
    var server_err = null;
    const collectsData = data_collection_args != null;
    if (collectsData) var data_col = await spawn(...data_collection_args);
    this.server = await spawn(...server_start_args);
    if (typeof this.server.pid !== "number") {
      this.server = null;
      if (collectsData) data_col.kill("SIGTERM");
      return false;
    }
    this.server.on("error", (err) => {
      server_err = err;
    });
    if (expected_server_output != null)
      this.server.stdout.on("data", (data) => {
        const stdout = data.toString();
        server_stdout += stdout;
      });

    if (server_err == null && collectsData)
      data_col.stdout.pipe(this.server.stdin);
    if (delay_in_ms) await delay(delay_in_ms);
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
    if (collectsData) data_col.kill("SIGTERM");
    if (stdoutCallBack) this.server.stdout.on("data", stdoutCallBack);
    return true;
  }

  async stop(delay_in_ms) {
    if (!this.server) return false;
    var exited = false;
    this.server.on("exit", (exit) => {
      exited = true;
    });
    await this.server.stdin.write("\x03");
    await this.server.stdin.end();
    await delay(500);
    const killed = await this.server.kill("SIGTERM");
    if (delay_in_ms) await delay(delay_in_ms);
    if (exited || this.server.exitCode != null) {
      this.server = null;
      return true;
    }
    return false;
  }
}
