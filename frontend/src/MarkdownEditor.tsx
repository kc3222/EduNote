import React, { useEffect, useRef } from "react";
import { MilkdownProvider, Milkdown, useEditor } from "@milkdown/react";
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx } from "@milkdown/core";
import { commonmark } from "@milkdown/preset-commonmark";

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
  const editorRef = useRef<Editor | null>(null);
  
  useEditor((root) => {
    const editor = Editor.make()
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
      .use(commonmark);
    
    editorRef.current = editor;
    return editor;
  });

  // Handle content changes and keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        onSave?.();
      }
    };

    // Set up content change listener using DOM events
    const handleContentChange = () => {
      if (editorRef.current && onContentChange) {
        // Get the current content from the editor
        const editorElement = document.querySelector('.prosemirror-editor');
        if (editorElement) {
          const content = editorElement.textContent || '';
          onContentChange(content);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    
    // Listen for input events on the editor
    const editorElement = document.querySelector('.prosemirror-editor');
    if (editorElement) {
      editorElement.addEventListener('input', handleContentChange);
      editorElement.addEventListener('paste', handleContentChange);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (editorElement) {
        editorElement.removeEventListener('input', handleContentChange);
        editorElement.removeEventListener('paste', handleContentChange);
      }
    };
  }, [onSave, onContentChange]);

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


