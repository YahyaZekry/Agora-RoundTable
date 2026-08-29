import { tool } from "@opencode-ai/plugin"
import { personaRoot, resolvePersonasDir, slugify, roundtablePresetsFile, roundtableSessionFile } from "../lib/data-dir.js"

export const AgoraPlugin = async (_ctx) => {
  return {
    tool: {
      // Resolve the shared Agora data dir — opencode-native, no Claude required.
      agora_data_dir: tool({
        description:
          "Resolve the Agora personas directory (opencode-native, with optional Claude-share fallback). Returns the resolved absolute path to the personas root plus the individual paths for session/preset files. Call this before building or loading any coach persona.",
        args: {},
        async execute() {
          const root = personaRoot()
          const personas = resolvePersonasDir()
          return {
            output: [
              `agora_root=${root}`,
              `personas=${personas}`,
              `presets=${roundtablePresetsFile()}`,
              `session=${roundtableSessionFile()}`,
            ].join("\n"),
          }
        },
      }),

      // Slugify a person's name the same way everywhere.
      agora_slugify: tool({
        description:
          "Slugify a person's name for Agora (lowercase, hyphens, e.g. 'Alex Hormozi' -> 'alex-hormozi').",
        args: {
          name: tool.schema.string().describe("The person's display name"),
        },
        async execute(args) {
          return `slug=${slugify(args.name)}`
        },
      }),

      // Read or write the roundtable session/presets JSON.
      agora_session: tool({
        description:
          "Read or write Agora session state as JSON. Use 'read' to load roundtable-session.json or roundtable-presets.json, 'write' to save the active roundtable coaches.",
        args: {
          action: tool.schema.enum(["read", "write"]),
          file: tool.schema
            .enum(["session", "presets"])
            .describe("Which state file"),
          data: tool.schema
            .optional(tool.schema.record(tool.schema.string(), tool.schema.any()))
            .describe(
              "Required for 'write': the JSON value to persist (e.g. { coaches: [{slug,name}] })"
            ),
        },
        async execute(args, c) {
          const { readFile, writeFile, mkdir } = await import("node:fs/promises")
          const path = args.file === "session" ? roundtableSessionFile() : roundtablePresetsFile()
          if (args.action === "read") {
            try {
              return await readFile(path, "utf8")
            } catch {
              return "{}"
            }
          }
          await mkdir(path.split("/").slice(0, -1).join("/"), { recursive: true })
          await writeFile(path, JSON.stringify(args.data, null, 2))
          return `wrote ${path}`
        },
      }),
    },
  }
}
