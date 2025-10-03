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

  return <Milkdown />;
}

export default function MarkdownEditor(props: MarkdownEditorProps) {
  const { className } = props;
  return (
    <div className={className} style={{ height: "100%" }}>
      <MilkdownProvider>
        <InnerEditor {...props} />
      </MilkdownProvider>
    </div>
  );
}


