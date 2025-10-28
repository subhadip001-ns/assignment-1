# Frontend — Student Course Enrollment Portal

Modern React + TypeScript SPA for managing students, courses, enrollments, and an AI assistant.

## Stack

- React 19 (functional components) + TypeScript
- Vite 7
- TanStack Router (`@tanstack/react-router`)
- Tailwind CSS v4
- shadcn/ui primitives (Radix UI) and `lucide-react`
- Axios for API calls

## Prerequisites

- Node.js 18+ (recommended LTS)
- pnpm 9+

## Getting Started

```bash
cd frontend
pnpm install
pnpm dev
```

The app runs at `http://localhost:5173` (default Vite port). The backend API is expected at `http://localhost:8000`.

### API Base URL

The base URL is currently defined in `src/lib/api.ts`:

```ts
const API_BASE_URL = 'http://localhost:8000';
```

Update this value if your backend runs elsewhere.

## Available Scripts

- `pnpm dev`: start development server
- `pnpm build`: type-check and build for production
- `pnpm preview`: preview production build
- `pnpm lint`: run ESLint

## Routes and Access

- `/login` (public)
- `/` (dashboard, authenticated)
- `/browse-courses` (students, authenticated)
- `/ai-chat` (authenticated)
- `/students` (admin only)
- `/courses` (admin only)
- `/enrollments` (admin only)

Auth is handled via `src/lib/auth.tsx` with token and user in `localStorage`. Route guarding is implemented by `src/components/ProtectedRoute.tsx`.

## Project Structure

```
src/
├── components/            # Layout, guards, and UI wrappers
├── lib/                   # API client, auth provider, utils, types
├── routes/                # Route components (functional)
├── components/ui/         # shadcn/ui primitives
└── main.tsx               # App bootstrap
```

## Building

```bash
pnpm build
pnpm preview
```

## Linting

```bash
pnpm lint
```

## Notes

- Uses functional React components exclusively.
- Tailwind v4 is configured; utility classes are used throughout.
