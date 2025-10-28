import { createRouter, createRoute, createRootRoute, Outlet } from '@tanstack/react-router'
import { Dashboard } from './routes/Dashboard'
import { Students } from './routes/Students'
import { Courses } from './routes/Courses'
import { Enrollments } from './routes/Enrollments'
import { Login } from './routes/Login'
import { CourseBrowser } from './routes/CourseBrowser'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'

// Create root route
const rootRoute = createRootRoute({
  component: () => <Outlet />,
})

// Create login route (public)
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: Login,
})

// Create protected routes wrapper
const protectedRoutes = createRoute({
  getParentRoute: () => rootRoute,
  id: 'protected',
  component: () => (
    <ProtectedRoute>
      <Layout />
    </ProtectedRoute>
  ),
})

// Create admin-only routes wrapper
const adminRoutes = createRoute({
  getParentRoute: () => protectedRoutes,
  id: 'admin',
  component: () => (
    <ProtectedRoute requireAdmin>
      <Outlet />
    </ProtectedRoute>
  ),
})

// Create index route (protected)
const indexRoute = createRoute({
  getParentRoute: () => protectedRoutes,
  path: '/',
  component: Dashboard,
})

// Create course browser route (protected - for students)
const courseBrowserRoute = createRoute({
  getParentRoute: () => protectedRoutes,
  path: '/browse-courses',
  component: CourseBrowser,
})

// Create students route (admin only)
const studentsRoute = createRoute({
  getParentRoute: () => adminRoutes,
  path: '/students',
  component: Students,
})

// Create courses route (admin only)
const coursesRoute = createRoute({
  getParentRoute: () => adminRoutes,
  path: '/courses',
  component: Courses,
})

// Create enrollments route (admin only)
const enrollmentsRoute = createRoute({
  getParentRoute: () => adminRoutes,
  path: '/enrollments',
  component: Enrollments,
})

// Create the route tree
const routeTree = rootRoute.addChildren([
  loginRoute,
  protectedRoutes.addChildren([
    indexRoute,
    courseBrowserRoute,
    adminRoutes.addChildren([
      studentsRoute,
      coursesRoute,
      enrollmentsRoute,
    ]),
  ]),
])

// Create the router
export const router = createRouter({
  routeTree,
})

// Register the router for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
