import React, { useEffect, useRef } from "react";
import { MilkdownProvider, Milkdown, useEditor } from "@milkdown/react";
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx } from "@milkdown/core";
import { commonmark } from "@milkdown/preset-commonmark";
import { listener, listenerCtx } from "@milkdown/plugin-listener";
import { getMarkdown, replaceAll } from "@milkdown/utils";

// import "./editorSnowStorm.css";
import "./editor.css"
// import "./editorNordDark.css";

type MarkdownEditorProps = {
  initialMarkdown?: string;
  editable?: boolean;
  ariaLabel?: string;
  className?: string;
  style?: React.CSSProperties;
  onContentChange?: (content: string) => void;   // markdown string
  onSave?: (content?: string) => void;           // markdown string (optional)
};

function InnerEditor({
  initialMarkdown,
  editable = true,
  ariaLabel = "Markdown editor",
  onContentChange,
  onSave
}: MarkdownEditorProps) {
  const editorRef = useRef<Editor | null>(null);

  useEditor((root) => {
    const editor = Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, root);
        ctx.set(
          defaultValueCtx,
          initialMarkdown ??
            "# Notes\n\nType `#` then a space to create a heading.\n\n- Item 1\n- Item 2"
        );
        ctx.set(editorViewOptionsCtx, {
          editable: () => editable,
          attributes: {
            "aria-label": ariaLabel,
            class: "prosemirror-editor",
          },
        });

        // Wire up live markdown updates (fires on every doc change).
        ctx.get(listenerCtx)
          .markdownUpdated((_, md) => {
            onContentChange?.(md);          // <-- this is the canonical markdown string
          });
      })
      .use(commonmark)
      .use(listener);

    editorRef.current = editor;
    return editor;
  });

  // Handle Cmd/Ctrl+S -> call onSave with the latest markdown
  useEffect(() => {
    const onKeyDown = async (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        const md = await editorRef.current?.action(getMarkdown());
        onSave?.(md);
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onSave]);

  // Note: We don't need to manually update the editor content when initialMarkdown changes
  // because the editor is recreated with the new key when switching notes

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
        ...style,
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