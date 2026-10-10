// Agora RoundTable plugin for OpenCode.
//
// NOTE: deliberately a raw object default export (no `Plugin.define` import) —
// OpenCode's loader accepts plain `{ id, setup }` and failed to resolve the
// `@opencode/plugin` bare specifier in its own module environment. The setup
// context (`ctx.tool`) is provided by the loader.
import { personaRoot, resolvePersonasDir, slugify, roundtablePresetsFile, roundtableSessionFile } from "../lib/data-dir.js"

export default {
  id: "agora-roundtable",
  async setup(ctx) {
    await ctx.tool.transform((editor) => {
      editor.namespace({
        name: "agora",
        description: "Agora RoundTable data helpers — resolve the shared persona data dir, slugify names, and read/write roundtable session state.",
      })

      // Resolve the shared Agora data dir — opencode-native, no Claude required.
      editor.add({
        name: "data_dir",
        description:
          "Resolve the Agora personas directory (opencode-native, with optional Claude-share fallback). Returns the resolved absolute path to the personas root plus the individual paths for session/preset files. Call this before building or loading any coach persona.",
        input: { type: "object", properties: {}, additionalProperties: false },
        options: { namespace: "agora", codemode: true },
        async execute() {
          const root = personaRoot()
          const personas = resolvePersonasDir()
          return {
            content: [
              `agora_root=${root}`,
              `personas=${personas}`,
              `presets=${roundtablePresetsFile()}`,
              `session=${roundtableSessionFile()}`,
            ].join("\n"),
          }
        },
      })

      // Slugify a person's name the same way everywhere.
      editor.add({
        name: "slugify",
        description:
          "Slugify a person's name for Agora (lowercase, hyphens, e.g. 'Alex Hormozi' -> 'alex-hormozi').",
        input: {
          type: "object",
          properties: {
            name: { type: "string", description: "The person's display name" },
          },
          required: ["name"],
          additionalProperties: false,
        },
        options: { namespace: "agora", codemode: true },
        async execute(args) {
          return { content: `slug=${slugify(args.name)}` }
        },
      })

      // Read or write the roundtable session/presets JSON.
      editor.add({
        name: "session",
        description:
          "Read or write Agora session state as JSON. Use 'read' to load roundtable-session.json or roundtable-presets.json, 'write' to save the active roundtable coaches.",
        input: {
          type: "object",
          properties: {
            action: { type: "string", enum: ["read", "write"], description: "Which operation to perform" },
            file: { type: "string", enum: ["session", "presets"], description: "Which state file" },
            data: {
              type: "object",
              description: "Required for 'write': the JSON value to persist (e.g. { coaches: [{slug,name}] })",
            },
          },
          required: ["action", "file"],
          additionalProperties: false,
        },
        options: { namespace: "agora", codemode: true },
        async execute(args) {
          const { readFile, writeFile, mkdir } = await import("node:fs/promises")
          const path = args.file === "session" ? roundtableSessionFile() : roundtablePresetsFile()
          if (args.action === "read") {
            try {
              return { content: await readFile(path, "utf8") }
            } catch {
              return { content: "{}" }
            }
          }
          if (!args.data) {
            return { content: "error: 'write' requires the data argument" }
          }
          await mkdir(path.split("/").slice(0, -1).join("/"), { recursive: true })
          await writeFile(path, JSON.stringify(args.data, null, 2))
          return { content: `wrote ${path}` }
        },
      })
    })
  },
}