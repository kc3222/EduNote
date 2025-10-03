// MilkdownTestPage.tsx (Milkdown v7 pattern)
import React from "react";
import { MilkdownProvider, Milkdown, useEditor } from "@milkdown/react";
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx } from "@milkdown/core";
import { commonmark } from "@milkdown/preset-commonmark";
// import "./editor.css";
import "./editorSnowStorm.css";

function InnerEditor() {
  useEditor((root) =>
    Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, root);
        ctx.set(defaultValueCtx, "# Milkdown\n\nType `#` then a space to create a heading.\n\n- Item 1\n- Item 2");
        ctx.set(editorViewOptionsCtx, {
          editable: () => true,
          attributes: {
            "aria-label": "Milkdown editor",
            class: "prosemirror-editor",
          },
        });
      })
      .use(commonmark)
  );

  // Render the editor view
  return <Milkdown />;
}

export default function MilkdownTestPage() {
  return (
    <div style={{ height: "100vh", display: "grid", gridTemplateRows: "auto 1fr" }}>
      <header style={{ padding: 12, borderBottom: "1px solid #e2e8f0", background: "#fff" }}>
        <strong>Milkdown v7 Test</strong>
        <span style={{ marginLeft: 12, color: "#64748b" }}>CommonMark preset</span>
      </header>
      <main style={{ padding: 12 }}>
        <div style={{ height: "100%", border: "1px solid #e2e8f0", borderRadius: 12, overflow: "hidden", background: "#fff" }}>
          <MilkdownProvider>
            <InnerEditor />
          </MilkdownProvider>
        </div>
      </main>
    </div>
  );
}


