import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

const HOOK_SCRIPT =
  process.env.FF_STOP_HOOK_SCRIPT || path.join(os.homedir(), ".ai-hooks", "ff-stop-hook.mjs");

function runHook(payload) {
  return new Promise((resolve) => {
    const child = spawn("node", [HOOK_SCRIPT, "--opencode"], {
      stdio: ["pipe", "pipe", "ignore"],
      windowsHide: true,
    });

    let stdout = "";
    child.stdout.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.on("error", () => resolve({ action: "allow" }));
    child.on("close", () => {
      try {
        resolve(JSON.parse(stdout || "{}"));
      } catch {
        resolve({ action: "allow" });
      }
    });

    child.stdin.end(JSON.stringify(payload));
  });
}

export const FFStopGate = async ({ client, directory, worktree }) => {
  const continued = new Set();

  return {
    event: async ({ event }) => {
      const part = event.properties?.part;
      const isIdle = event.type === "session.idle";
      const isStopStep =
        event.type === "message.part.updated" && part?.type === "step-finish" && part?.reason === "stop";
      if (!isIdle && !isStopStep) return;

      const sessionID = event.properties?.sessionID || part?.sessionID;
      if (!sessionID || continued.has(sessionID)) return;

      let cwd = event.properties?.directory || directory || worktree || process.cwd();
      try {
        const response = await client.session.get({ path: { id: sessionID } });
        const session = response?.data ?? response;
        cwd = session?.directory || session?.info?.directory || session?.path?.cwd || cwd;
      } catch {
        // Fall back to the plugin context directory.
      }

      const result = await runHook({
        cwd,
        directory: cwd,
        session_id: sessionID,
        hook_event_name: "Stop",
        stop_hook_active: continued.has(sessionID),
      });

      if (result.action !== "continue" || !result.prompt) return;

      continued.add(sessionID);
      await client.session.prompt({
        path: { id: sessionID },
        body: {
          parts: [
            {
              type: "text",
              text: result.prompt,
            },
          ],
        },
      });
    },
  };
};
