import React, { useEffect, useRef, useState } from "react";
import { MilkdownProvider, Milkdown, useEditor } from "@milkdown/react";
import { Editor, rootCtx, defaultValueCtx, editorViewOptionsCtx, editorViewCtx } from "@milkdown/core";
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
  initialFontSize?: string;
  initialFontFamily?: string;
  initialLineHeight?: string;
  onStylingChange?: (styling: { fontSize: string; fontFamily: string; lineHeight: string }) => void;
};

type InnerEditorProps = MarkdownEditorProps & {
  onEditorReady?: (editor: Editor | null) => void;
};

const DEFAULT_FONT_SIZE = "16px";
const DEFAULT_FONT_FAMILY =
  "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif";
const DEFAULT_LINE_HEIGHT = "1.65";

const FONT_SIZE_OPTIONS = [
  { label: "Small", value: "14px" },
  { label: "Normal", value: "16px" },
  { label: "Large", value: "18px" },
  { label: "Extra Large", value: "20px" },
  { label: "Presentation", value: "24px" },
];

const FONT_FAMILY_OPTIONS = [
  { label: "Sans", value: DEFAULT_FONT_FAMILY },
  { label: "Serif", value: "Georgia, 'Times New Roman', serif" },
  { label: "Mono", value: "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace" },
];

const LINE_HEIGHT_OPTIONS = [
  { label: "Compact", value: "1.4" },
  { label: "Comfort", value: "1.65" },
  { label: "Roomy", value: "1.85" },
];

function InnerEditor({
  initialMarkdown,
  editable = true,
  ariaLabel = "Markdown editor",
  onContentChange,
  onSave,
  onEditorReady,
}: InnerEditorProps) {
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
    onEditorReady?.(editor);
    return editor;
  });

  useEffect(() => {
    return () => {
      onEditorReady?.(null);
    };
  }, [onEditorReady]);

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
  const { className, style, initialFontSize, initialFontFamily, initialLineHeight, onStylingChange } = props;
  const [fontSize, setFontSize] = useState(initialFontSize || DEFAULT_FONT_SIZE);
  const [fontFamily, setFontFamily] = useState(initialFontFamily || DEFAULT_FONT_FAMILY);
  const [lineHeight, setLineHeight] = useState(initialLineHeight || DEFAULT_LINE_HEIGHT);
  const editorRef = useRef<Editor | null>(null);

  // Update state when initial props change
  useEffect(() => {
    if (initialFontSize) setFontSize(initialFontSize);
    if (initialFontFamily) setFontFamily(initialFontFamily);
    if (initialLineHeight) setLineHeight(initialLineHeight);
  }, [initialFontSize, initialFontFamily, initialLineHeight]);

  // Notify parent when styling changes
  const handleFontSizeChange = (newSize: string) => {
    setFontSize(newSize);
    onStylingChange?.({ fontSize: newSize, fontFamily, lineHeight });
  };

  const handleFontFamilyChange = (newFamily: string) => {
    setFontFamily(newFamily);
    onStylingChange?.({ fontSize, fontFamily: newFamily, lineHeight });
  };

  const handleLineHeightChange = (newHeight: string) => {
    setLineHeight(newHeight);
    onStylingChange?.({ fontSize, fontFamily, lineHeight: newHeight });
  };

  // CSS variables for editor-wide formatting
  const editorVariablesStyle = {
    "--md-font-size": fontSize,
    "--md-font-family": fontFamily,
    "--md-line-height": lineHeight,
  } as React.CSSProperties;

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
      <div className="markdown-toolbar" role="toolbar" aria-label="Markdown editor formatting toolbar">
        <div className="markdown-toolbar__group">
          <label htmlFor="font-size-select" className="markdown-toolbar__label">Font size</label>
          <select
            id="font-size-select"
            className="markdown-toolbar__select"
            value={fontSize}
            onChange={(e) => handleFontSizeChange(e.target.value)}
          >
            {FONT_SIZE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="markdown-toolbar__group">
          <label htmlFor="font-family-select" className="markdown-toolbar__label">Font style</label>
          <select
            id="font-family-select"
            className="markdown-toolbar__select"
            value={fontFamily}
            onChange={(e) => handleFontFamilyChange(e.target.value)}
          >
            {FONT_FAMILY_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div className="markdown-toolbar__group">
          <label htmlFor="line-height-select" className="markdown-toolbar__label">Line spacing</label>
          <select
            id="line-height-select"
            className="markdown-toolbar__select"
            value={lineHeight}
            onChange={(e) => handleLineHeightChange(e.target.value)}
          >
            {LINE_HEIGHT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <MilkdownProvider>
        <div
          style={{
            height: "100%",
            display: "flex",
            flexDirection: "column",
            flex: 1,
            ...editorVariablesStyle,
          }}
        >
          <InnerEditor
            {...props}
            onEditorReady={(editor) => {
              editorRef.current = editor;
            }}
          />
        </div>
      </MilkdownProvider>
    </div>
  );
}