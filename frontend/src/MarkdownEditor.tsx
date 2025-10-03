import React from "react";
import { MilkdownProvider, Milkdown, useEditor } from "@milkdown/react";
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx } from "@milkdown/core";
import { commonmark } from "@milkdown/preset-commonmark";

// Use one of the provided editor themes
// import "./editorSnowStorm.css";
import "./editor.css"
// import "./editorNordDark.css";

type MarkdownEditorProps = {
  initialMarkdown?: string;
  editable?: boolean;
  ariaLabel?: string;
  className?: string;
  style?: React.CSSProperties;
};

function InnerEditor({ initialMarkdown, editable = true, ariaLabel = "Markdown editor" }: MarkdownEditorProps) {
  useEditor((root) =>
    Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, root);
        ctx.set(
          defaultValueCtx,
          initialMarkdown ?? "# Notes\n\nType `#` then a space to create a heading.\n\n- Item 1\n- Item 2"
        );
        ctx.set(editorViewOptionsCtx, {
          editable: () => editable,
          attributes: {
            "aria-label": ariaLabel,
            class: "prosemirror-editor",
          },
        });
      })
      .use(commonmark)
  );

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", flex: 1 }}>
      <Milkdown />
    </div>
  );
}

export default function MarkdownEditor(props: MarkdownEditorProps) {
  const { className, style } = props;
  return (
    <div 
      className={className} 
      style={{ 
        height: "100%", 
        display: "flex", 
        flexDirection: "column",
        ...style 
      }}
    >
      <MilkdownProvider>
        <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
          <InnerEditor {...props} />
        </div>
      </MilkdownProvider>
    </div>
  );
}


