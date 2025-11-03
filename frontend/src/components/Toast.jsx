import { useEffect } from "react";
import { CheckCircle, XCircle, X } from "lucide-react";

export default function Toast({ message, type = "success", onClose, duration = 3000 }) {
  useEffect(() => {
    if (message && duration > 0) {
      const timer = setTimeout(() => {
        onClose?.();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [message, duration, onClose]);

  if (!message) return null;

  const isError = type === "error" || message.toLowerCase().includes("error");
  
  return (
    <div className="fixed top-4 right-4 z-50 toast-enter">
      <div className={`
        flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg ring-1 backdrop-blur
        ${isError 
          ? "bg-red-50 ring-red-200 text-red-800" 
          : "bg-green-50 ring-green-200 text-green-800"
        }
        min-w-[280px] max-w-md
      `}>
        <div className="flex-shrink-0">
          {isError ? (
            <XCircle className="h-5 w-5 text-red-600" />
          ) : (
            <CheckCircle className="h-5 w-5 text-green-600" />
          )}
        </div>
        <p className="flex-1 text-sm font-medium">{message}</p>
        <button
          onClick={onClose}
          className={`
            flex-shrink-0 p-1 rounded-lg hover:bg-opacity-20 transition-colors
            ${isError ? "hover:bg-red-200" : "hover:bg-green-200"}
          `}
          aria-label="Close notification"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

