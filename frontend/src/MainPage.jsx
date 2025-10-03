import React, { useState } from "react";
import MarkdownEditor from "./MarkdownEditor";
import { Search, Upload, Save, Eye, Plus, ChevronLeft, ChevronRight, FileText, ListChecks, Layers, HelpCircle, LogOut, NotebookPen, Edit3, BookOpen, MessageCircle, ChevronDown, ChevronRight as ChevronRightIcon } from "lucide-react";
import EduNoteIcon from "./assets/EduNoteIcon.jpg";

export default function MainPage({ user, onLogout }) {
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [expandedLectures, setExpandedLectures] = useState({});
  const [activeContent, setActiveContent] = useState(null);

  const leftW = leftOpen ? "w-80" : "w-[64px]";
  const rightW = rightOpen ? "w-[64px]" : "w-[24px]";

  const lectures = [
    {
      id: 1,
      title: "Lecture 1 - Introduction to Data Structures",
      quizzes: [
        { id: 1, title: "Quiz 1: Key Concepts" },
        { id: 2, title: "Quiz 2: Terminology" }
      ],
      flashcards: [
        { id: 1, title: "Flashcards: Definitions" }
      ],
      summary: [
        { id: 1, title: "Summary: Key Concepts" }
      ]
    },
    {
      id: 2,
      title: "Lecture 2 - Arrays and Linked Lists",
      quizzes: [
        { id: 1, title: "Quiz 1: Array Basics" },
        { id: 2, title: "Quiz 2: Linked List Operations" },
        { id: 3, title: "Quiz 3: Time Complexity" }
      ],
      flashcards: [
        { id: 1, title: "Flashcards: Array Methods" },
        { id: 2, title: "Flashcards: Linked List Terms" }
      ],
      summary: [
        { id: 1, title: "Summary: Array Operations" }
      ]
    },
    {
      id: 3,
      title: "Lecture 3 - Basic Concepts",
      // No quizzes, flashcards, or summary - testing empty states
      quizzes: [],
      flashcards: null,
      summary: undefined
    },
    {
      id: 4,
      title: "Lecture 4 - Advanced Topics",
      quizzes: [
        { id: 1, title: "Quiz 1: Advanced Concepts" }
      ],
      // No flashcards or summary
      flashcards: [],
      summary: null
    }
  ];

  const toggleLecture = (lectureId) => {
    setExpandedLectures(prev => ({
      ...prev,
      [lectureId]: !prev[lectureId]
    }));
  };

  const handleQuizClick = (lectureId, quizId) => {
    setActiveContent({ lectureId, type: 'quiz', id: quizId });
  };

  const handleFlashcardClick = (lectureId, cardId) => {
    setActiveContent({ lectureId, type: 'flashcard', id: cardId });
  };

  const handleSummaryClick = (lectureId, summaryId) => {
    setActiveContent({ lectureId, type: 'summary', id: summaryId });
  };

  // Helper function to check if array has content
  const hasContent = (array) => {
    return array && Array.isArray(array) && array.length > 0;
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#F7FAFF] via-[#F4FBF7] to-[#F2FAFF] text-slate-700">
      <TopBar user={user} onLogout={onLogout} />
      <div className="w-full px-2 pb-2">
        <div className={`mt-2 flex gap-2`}>
          {/* Left Sidebar */}
          <aside className={`${leftW} transition-all duration-300 relative`}>
            <div className="sticky top-2">
              <div className="rounded-2xl bg-white/90 shadow-sm ring-1 ring-slate-100 backdrop-blur p-4 h-[calc(100vh-80px)] flex flex-col">
                {leftOpen ? (
                  <>
                    <div className="mb-3 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <NotebookPen className="h-4 w-4" />
                        <span className="font-medium text-slate-800 text-sm">My Notes</span>
                      </div>
                      <button className="inline-flex items-center gap-2 rounded-xl bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-100" onClick={() => setLeftOpen(false)}>
                        <Plus className="h-3 w-3" /> Add
                      </button>
                    </div>
                    <div className="space-y-2 overflow-auto pr-1">
                      {lectures.map((lecture) => (
                        <div key={lecture.id} className="space-y-1">
                          {/* Lecture Header */}
                          <div className="rounded-xl border border-slate-200 bg-white p-2">
                            <button
                              onClick={() => toggleLecture(lecture.id)}
                              className="w-full flex items-center justify-between text-left"
                            >
                              <div className="flex items-center gap-2 min-w-0 flex-1">
                                {expandedLectures[lecture.id] ? (
                                  <ChevronDown className="h-3 w-3 text-slate-500 flex-shrink-0" />
                                ) : (
                                  <ChevronRightIcon className="h-3 w-3 text-slate-500 flex-shrink-0" />
                                )}
                                <span className="font-medium text-slate-800 text-xs truncate">
                                  {lecture.title}
                                </span>
                              </div>
                            </button>
                            
                            {/* SUMMARY, QUIZZES and FLASHCARDS Sections */}
                            {expandedLectures[lecture.id] && (
                              <div className="mt-2 space-y-3">
                                {/* SUMMARY Section - only show if has content */}
                                {hasContent(lecture.summary) && (
                                  <div>
                                    <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">
                                      SUMMARY
                                    </h3>
                                    <div className="space-y-1">
                                      {lecture.summary.map((summary) => (
                                        <button
                                          key={summary.id}
                                          onClick={() => handleSummaryClick(lecture.id, summary.id)}
                                          className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-50 text-left"
                                        >
                                          <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                                            <FileText className="h-2.5 w-2.5 text-blue-600" />
                                          </div>
                                          <span className="text-xs text-slate-700 font-medium truncate">
                                            {summary.title}
                                          </span>
                                        </button>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* QUIZZES Section - only show if has content */}
                                {hasContent(lecture.quizzes) && (
                                  <div>
                                    <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">
                                      QUIZZES
                                    </h3>
                                    <div className="space-y-1">
                                      {lecture.quizzes.map((quiz) => (
                                        <button
                                          key={quiz.id}
                                          onClick={() => handleQuizClick(lecture.id, quiz.id)}
                                          className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-50 text-left"
                                        >
                                          <div className="w-5 h-5 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                                            <HelpCircle className="h-2.5 w-2.5 text-red-600" />
                                          </div>
                                          <span className="text-xs text-slate-700 font-medium truncate">
                                            {quiz.title}
                                          </span>
                                        </button>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* FLASHCARDS Section - only show if has content */}
                                {hasContent(lecture.flashcards) && (
                                  <div>
                                    <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1">
                                      FLASHCARDS
                                    </h3>
                                    <div className="space-y-1">
                                      {lecture.flashcards.map((card) => (
                                        <button
                                          key={card.id}
                                          onClick={() => handleFlashcardClick(lecture.id, card.id)}
                                          className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-50 text-left"
                                        >
                                          <div className="w-5 h-5 rounded-full bg-white border border-slate-200 flex items-center justify-center flex-shrink-0">
                                            <span className="text-slate-600 text-xs">♠</span>
                                          </div>
                                          <span className="text-xs text-slate-700 font-medium truncate">
                                            {card.title}
                                          </span>
                                        </button>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Show message if no content available */}
                                {!hasContent(lecture.summary) && !hasContent(lecture.quizzes) && !hasContent(lecture.flashcards) && (
                                  <div className="text-center py-4">
                                    <p className="text-xs text-slate-400 italic">No content available</p>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <RailButton icon={<NotebookPen className="h-4 w-4" />} label="Notes" showLabel={true} />
                  </div>
                )}
                <button
                  className="absolute -right-3 top-6 grid h-6 w-6 place-items-center rounded-full bg-white ring-1 ring-slate-200 shadow hover:bg-slate-50"
                  aria-label={leftOpen ? "Collapse sidebar" : "Expand sidebar"}
                  onClick={() => setLeftOpen((v) => !v)}
                >
                  {leftOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </button>
              </div>
            </div>
          </aside>

          {/* Center area (Editor + PDF) */}
          <main className={`flex-1 grid grid-cols-1 lg:grid-cols-2 gap-2`}>
            <section className="rounded-2xl bg-white/90 shadow-sm ring-1 ring-slate-100 backdrop-blur p-4">
              <div className="flex items-center justify-between">
                <div className="text-sm text-slate-500">
                  Editing: <span className="font-semibold text-slate-800">Lecture 1</span>
                </div>
                <div className="flex items-center gap-2">
                  <button className="inline-flex items-center gap-2 rounded-xl bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-100">
                    <Save className="h-4 w-4" /> Save
                  </button>
                  <button className="inline-flex items-center gap-2 rounded-xl bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-100">
                    <Eye className="h-4 w-4" /> Preview
                  </button>
                </div>
              </div>
              <div className="mt-3 rounded-xl border border-slate-200 bg-white h-[calc(100vh-180px)] overflow-hidden">
                <MarkdownEditor className="h-full" />
              </div>
            </section>

            <section className="rounded-2xl bg-white/90 shadow-sm ring-1 ring-slate-100 backdrop-blur p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <FileText className="h-4 w-4" /> PDF Viewer
                </div>
                <button className="inline-flex items-center gap-2 rounded-xl bg-slate-50 px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-100">
                  <Upload className="h-4 w-4" /> Upload
                </button>
              </div>
              <div className="mt-3 rounded-xl border border-slate-200 h-[calc(100vh-180px)] bg-gradient-to-br from-white to-emerald-50 grid place-items-center text-slate-400 italic text-sm">
                [PDF Viewer Area]
              </div>
            </section>
          </main>

          {/* Right Toolbar */}
          <aside className={`${rightW} transition-all duration-300`}>
            <div className="sticky top-2">
              <div className="relative rounded-2xl bg-white/90 shadow-sm ring-1 ring-slate-100 backdrop-blur py-3 flex flex-col items-center gap-3 h-[calc(100vh-80px)]">
                <button
                  className="absolute -left-3 top-4 grid h-6 w-6 place-items-center rounded-full bg-white ring-1 ring-slate-200 shadow hover:bg-slate-50"
                  aria-label={rightOpen ? "Collapse right rail" : "Expand right rail"}
                  onClick={() => setRightOpen((v) => !v)}
                >
                  {rightOpen ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
                </button>
                <RailButton icon={<FileText className="h-4 w-4" />} label="Summary" showLabel={rightOpen} />
                <RailButton icon={<ListChecks className="h-4 w-4" />} label="Quizzes" showLabel={rightOpen} />
                <RailButton icon={<Layers className="h-4 w-4" />} label="Flashcards" showLabel={rightOpen} />
                <RailButton icon={<MessageCircle className="h-4 w-4" />} label="Chat" showLabel={rightOpen} />
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

function TopBar({ user, onLogout }) {
  return (
    <header className="sticky top-0 z-20 bg-white/80 backdrop-blur">
      <div className="w-full flex items-center gap-6 px-2 py-2">
        {/* Logo/Brand */}
        <div className="flex items-center gap-2 pr-1">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-white ring-1 ring-slate-200 shadow-sm text-slate-700">
            <img src={EduNoteIcon} alt="EduNote" className="h-5 w-5 object-contain" />
          </div>
          <span className="text-lg font-semibold text-slate-800">EduNote</span>
        </div>
        
        {/* Search bar centered */}
        <div className="flex-1 flex justify-center">
          <div className="w-full max-w-md">
            <div className="flex items-center rounded-full bg-white ring-1 ring-slate-200 px-4 py-2 shadow-[inset_0_1px_0_0_rgba(0,0,0,0.02)]">
              <Search className="h-4 w-4 text-slate-400" />
              <input className="ml-2 w-full bg-transparent text-sm outline-none placeholder:text-slate-400" placeholder="Search notes..." />
            </div>
          </div>
        </div>
        
        {/* User info and sign out button */}
        <div className="flex items-center gap-3">
          <button 
            onClick={onLogout}
            className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50 shadow-sm"
          >
            <LogOut className="h-4 w-4" /><span>Sign&nbsp;out</span>
          </button>
        </div>
      </div>
    </header>
  );
}

function NavTab({ label, icon: Icon, active = false }) {
  return (
    <button
      className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ring-1 transition ${
        active
          ? "bg-white text-slate-800 ring-slate-200 shadow-sm"
          : "bg-transparent text-slate-600 ring-slate-200 hover:bg-white/60"
      }`}
    >
      <Icon className="h-4 w-4" />
      {label}
    </button>
  );
}

function RailButton({ icon, label, showLabel }) {
  return (
    <button className={`group w-[52px] ${showLabel ? "mb-1" : "mb-0"} flex flex-col items-center gap-1 text-[11px] font-medium text-slate-600 focus:outline-none`}>
      <div className="grid h-10 w-10 place-items-center rounded-xl bg-slate-50 ring-1 ring-slate-200 shadow-sm group-hover:bg-slate-100">
        {icon}
      </div>
      {showLabel && <span>{label}</span>}
    </button>
  );
}