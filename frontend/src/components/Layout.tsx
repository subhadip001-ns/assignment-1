import { Link, Outlet, useNavigate, useLocation } from '@tanstack/react-router'
import {
  Users,
  BookOpen,
  UserCheck,
  Home,
  LogOut,
  GraduationCap,
  MessageSquare,
} from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarSeparator,
  SidebarTrigger,
} from '@/components/ui/sidebar'
import { useAuth } from '@/lib/auth'

export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate({ to: '/login' })
  }

  const isAdmin = user?.role === 'admin'

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  const navLinks = [
    {
      to: '/',
      icon: Home,
      label: 'Dashboard',
      show: true,
    },
    {
      to: '/browse-courses',
      icon: GraduationCap,
      label: 'Browse Courses',
      show: !isAdmin,
    },
    {
      to: '/ai-chat',
      icon: MessageSquare,
      label: 'AI Chat',
      show: true,
    },
    {
      to: '/students',
      icon: Users,
      label: 'Students',
      show: isAdmin,
    },
    {
      to: '/courses',
      icon: BookOpen,
      label: 'Courses',
      show: isAdmin,
    },
    {
      to: '/enrollments',
      icon: UserCheck,
      label: 'Enrollments',
      show: isAdmin,
    },
  ]

  const filteredLinks = navLinks.filter((link) => link.show)

  return (
    <SidebarProvider>
      <Sidebar className=''>
        <SidebarHeader>
          <div className="flex items-center gap-2 px-2 py-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <GraduationCap className="h-4 w-4" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold">Enrollment Portal</span>
              <span className="text-xs text-muted-foreground">
                {isAdmin ? 'Admin' : 'Student'}
              </span>
            </div>
          </div>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Navigation</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {filteredLinks.map((link) => {
                  const Icon = link.icon
                  const active = isActive(link.to)
                  return (
                    <SidebarMenuItem key={link.to}>
                      <SidebarMenuButton
                        asChild
                        isActive={active}
                        tooltip={link.label}
                      >
                        <Link to={link.to}>
                          <Icon />
                          <span>{link.label}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  )
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <div className="flex items-center gap-2 px-2 py-2">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    {user?.name ? getInitials(user.name) : 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col min-w-0 flex-1">
                  <span className="text-sm font-medium truncate">
                    {user?.name || 'User'}
                  </span>
                  <span className="text-xs text-muted-foreground truncate">
                    {user?.role || 'student'}
                  </span>
                </div>
              </div>
            </SidebarMenuItem>
            <SidebarSeparator />
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={handleLogout}
                tooltip="Logout"
                className="w-full"
              >
                <LogOut />
                <span>Logout</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
      <SidebarInset>
        <header className="flex shrink-0 items-center gap-2 px-4 py-2">
          <SidebarTrigger className="-ml-1 cursor-pointer" />
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 md:p-6">
          <Outlet />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
