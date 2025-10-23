import React, { useState } from "react";
import { ArrowLeft, Plus, Trash2, Save } from "lucide-react";

export default function CreateFlashcardsPage({ onBack }) {
  const [flashcards, setFlashcards] = useState([{ front: "", back: "" }]);
  const [title, setTitle] = useState("Untitled Flashcard Set");

  const handleAddCard = () => {
    setFlashcards([...flashcards, { front: "", back: "" }]);
  };

  const handleDeleteCard = (index) => {
    setFlashcards(flashcards.filter((_, i) => i !== index));
  };

  const handleChange = (index, field, value) => {
    const updated = [...flashcards];
    updated[index][field] = value;
    setFlashcards(updated);
  };

  const handleSave = () => {
    console.log("Saved flashcards:", { title, flashcards });
    alert("Flashcards saved (console log only for now)");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F7FAFF] via-[#F4FBF7] to-[#F2FAFF] text-slate-700 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <button
            onClick={onBack}
            className="rounded-full bg-slate-100 p-2 hover:bg-slate-200 transition"
          >
            <ArrowLeft className="h-4 w-4 text-slate-600" />
          </button>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="text-lg font-semibold bg-transparent border-b border-slate-300 focus:border-blue-500 focus:outline-none"
          />
        </div>
        <button
          onClick={handleSave}
          className="inline-flex items-center gap-2 rounded-xl bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 ring-1 ring-blue-200 hover:bg-blue-100"
        >
          <Save className="h-4 w-4" /> Save Set
        </button>
      </div>

      {/* Flashcards List */}
      <div className="space-y-4">
        {flashcards.map((card, index) => (
          <div
            key={index}
            className="rounded-xl bg-white shadow-sm ring-1 ring-slate-200 p-4 flex flex-col gap-2 relative"
          >
            <button
              onClick={() => handleDeleteCard(index)}
              className="absolute top-2 right-2 text-red-400 hover:text-red-600"
              title="Delete card"
            >
              <Trash2 className="h-4 w-4" />
            </button>
            <textarea
              placeholder="Front (Question)"
              value={card.front}
              onChange={(e) => handleChange(index, "front", e.target.value)}
              className="w-full rounded-lg border border-slate-200 p-2 text-sm focus:ring-2 focus:ring-blue-200"
              rows={2}
            />
            <textarea
              placeholder="Back (Answer)"
              value={card.back}
              onChange={(e) => handleChange(index, "back", e.target.value)}
              className="w-full rounded-lg border border-slate-200 p-2 text-sm focus:ring-2 focus:ring-blue-200"
              rows={2}
            />
          </div>
        ))}
      </div>

      {/* Add Flashcard Button */}
      <div className="mt-4 flex justify-center">
        <button
          onClick={handleAddCard}
          className="inline-flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700 ring-1 ring-slate-200 hover:bg-slate-100"
        >
          <Plus className="h-4 w-4" /> Add Flashcard
        </button>
      </div>
    </div>
  );
}
