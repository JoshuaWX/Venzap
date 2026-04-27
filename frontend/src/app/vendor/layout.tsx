import { ChevronRight, Home, List, ShoppingBag, DollarSign, User as UserIcon, Bell, Menu } from "lucide-react";
import Link from "next/link";

export default function VendorLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-64 border-r bg-white">
        <div className="p-6 border-b flex items-center justify-between">
          <h2 className="text-xl font-bold tracking-tight text-primary">Venzap Vendor</h2>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          <Link href="/vendor/dashboard" className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-100">
            <Home className="mr-3 h-5 w-5 text-slate-500" />
            Dashboard
          </Link>
          <Link href="/vendor/orders" className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-100">
            <ShoppingBag className="mr-3 h-5 w-5 text-slate-500" />
            Orders
          </Link>
          <Link href="/vendor/catalogue" className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-100">
            <List className="mr-3 h-5 w-5 text-slate-500" />
            Catalogue
          </Link>
          <Link href="/vendor/earnings" className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-100">
            <DollarSign className="mr-3 h-5 w-5 text-slate-500" />
            Earnings
          </Link>
          <Link href="/vendor/profile" className="flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-slate-100">
            <UserIcon className="mr-3 h-5 w-5 text-slate-500" />
            Profile
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="flex h-16 items-center justify-between px-6 border-b bg-white">
          <div className="md:hidden">
            <Menu className="h-6 w-6 text-slate-600" />
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <button className="relative p-2 text-slate-400 hover:text-slate-500">
              <Bell className="h-6 w-6" />
              <span className="absolute top-1 right-1 h-2.5 w-2.5 rounded-full bg-red-500 border-2 border-white"></span>
            </button>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">Vendor Store</span>
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">
                V
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}