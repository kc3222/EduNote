# EduNote Frontend

A React + Vite application with Tailwind CSS for styling and Lucide React for icons.

## Prerequisites

- Node.js (version 16 or higher)
- npm or yarn package manager

## Setup Instructions

### 1. Install Dependencies

First, install the project dependencies:

```bash
npm install
```

### 2. Install Lucide React

Install Lucide React for beautiful, customizable SVG icons:

```bash
npm install lucide-react
```

**Usage Example:**
```jsx
import { Search, User, Settings } from 'lucide-react';

function MyComponent() {
  return (
    <div>
      <Search size={24} />
      <User className="text-blue-500" />
      <Settings strokeWidth={1.5} />
    </div>
  );
}
```

### 3. Install and Configure Tailwind CSS

Install Tailwind CSS and its dependencies:

```bash
npm install -D tailwindcss@^3.4.0 postcss autoprefixer
```

Initialize Tailwind CSS configuration:

```bash
npx tailwindcss init -p
```

This creates `tailwind.config.js` and `postcss.config.js` files.

**Configure Tailwind CSS:**
Update your `tailwind.config.js` to include your content paths:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Add Tailwind directives to your CSS:**
In your `src/index.css` file, add:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Development

To start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173` with hot module replacement (HMR) enabled.

## Adding New Service Servers

To add a new backend service, update the proxy configuration in `vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/auth": "http://localhost:8000",     // Auth service
      "/notes": "http://localhost:8001",    // Note service
      "/api/v2": "http://localhost:8002"    // New service
    }
  }
})
```

Then use relative URLs in your API calls:
```javascript
// Instead of: fetch('http://localhost:8002/api/v2/endpoint')
fetch('/api/v2/endpoint')
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Tech Stack

- **React** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **ESLint** - Code linting