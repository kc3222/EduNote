import React, { useEffect } from "react";
import { MilkdownProvider, Milkdown, useEditor } from "@milkdown/react";
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx } from "@milkdown/core";
import { commonmark } from "@milkdown/preset-commonmark";
import { listener, listenerCtx } from "@milkdown/plugin-listener";

// import "./editorSnowStorm.css";
import "./editor.css"
// import "./editorNordDark.css";

type MarkdownEditorProps = {
  initialMarkdown?: string;
  editable?: boolean;
  ariaLabel?: string;
  className?: string;
  style?: React.CSSProperties;
  onContentChange?: (content: string) => void;
  onSave?: () => void;
};

function InnerEditor({ initialMarkdown, editable = true, ariaLabel = "Markdown editor", onContentChange, onSave }: MarkdownEditorProps) {
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
        
        // Set up content change listener
        ctx.set(listenerCtx, {
          markdownUpdated: (ctx, markdown) => {
            onContentChange?.(markdown);
          },
        });
      })
      .use(commonmark)
      .use(listener)
  );

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        onSave?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onSave]);

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


