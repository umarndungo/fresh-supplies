import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { MobileNav } from "@/components/layout/mobile-nav";
import { NotificationMenu } from "@/components/layout/notification-menu";
import { ProfileDropdown } from "@/components/layout/profile-dropdown";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { LanguageSwitcher } from "@/components/layout/language-switcher";

export function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/80 px-4 backdrop-blur md:px-6">
      <MobileNav />
      <Breadcrumbs />
      <div className="ml-auto flex items-center gap-1">
        <LanguageSwitcher />
        <ThemeToggle />
        <NotificationMenu />
        <ProfileDropdown />
      </div>
    </header>
  );
}
