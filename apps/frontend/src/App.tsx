import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { MainLayout } from "./components/layout/MainLayout";
import { EnhancedAuthProvider } from "./contexts/EnhancedAuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { ProtectedRoute, InventoryRoute, FinanceRoute, HRRoute, StaffRoute } from "./components/auth/ProtectedRoute";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import { GlobalErrorProvider } from "./components/common/GlobalErrorHandler";

// Pages
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import ClientManagement from "./pages/ClientManagement";
import InventoryManagement from "./pages/InventoryManagement";
import FinanceManagement from "./pages/FinanceManagement";
import HRManagement from "./pages/HRManagement";
import Analytics from "./pages/Analytics";
import Scheduling from "./pages/Scheduling";
import Login from "./pages/Login";
import Services from "./pages/Services";
import ThemeManager from "./components/theme/ThemeManager";
import IPFSManager from "./components/ipfs/IPFSManager";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        // Retry up to 2 times for other errors
        return failureCount < 2;
      },
    },
  },
});

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <GlobalErrorProvider>
        <BrowserRouter>
          <EnhancedAuthProvider>
            <ThemeProvider>
              <TooltipProvider>
                    <Toaster />
                    <Sonner />
                    <Routes>
                      <Route path="/" element={<LandingPage />} />
                      <Route path="/login" element={<Login />} />
                      <Route path="/dashboard" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <Dashboard />
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      <Route path="/clients" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <ClientManagement />
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      <Route path="/scheduling" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <Scheduling />
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      <Route path="/inventory" element={
                        <InventoryRoute>
                          <MainLayout>
                            <InventoryManagement />
                          </MainLayout>
                        </InventoryRoute>
                      } />
                      <Route path="/finance" element={
                        <FinanceRoute>
                          <MainLayout>
                            <FinanceManagement />
                          </MainLayout>
                        </FinanceRoute>
                      } />
                      <Route path="/hr" element={
                        <HRRoute>
                          <MainLayout>
                            <HRManagement />
                          </MainLayout>
                        </HRRoute>
                      } />
                      <Route path="/analytics" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <Analytics />
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      <Route path="/reports" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <div className="p-8 text-center">
                              <h1 className="text-2xl font-bold mb-4">Reports</h1>
                              <p className="text-muted-foreground">Reports module coming soon...</p>
                            </div>
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      <Route path="/notifications" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <div className="p-8 text-center">
                              <h1 className="text-2xl font-bold mb-4">Notifications</h1>
                              <p className="text-muted-foreground">Notifications center coming soon...</p>
                            </div>
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      <Route path="/settings" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <div className="p-8 text-center">
                              <h1 className="text-2xl font-bold mb-4">Settings</h1>
                              <p className="text-muted-foreground">Settings panel coming soon...</p>
                            </div>
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      <Route path="/services" element={<Services />} />
                      <Route path="/admin/themes" element={
                        <StaffRoute>
                          <MainLayout>
                            <ThemeManager />
                          </MainLayout>
                        </StaffRoute>
                      } />
                      <Route path="/files" element={
                        <ProtectedRoute>
                          <MainLayout>
                            <IPFSManager />
                          </MainLayout>
                        </ProtectedRoute>
                      } />
                      
                      {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                      <Route path="*" element={<NotFound />} />
                    </Routes>
                  </TooltipProvider>
              </ThemeProvider>
          </EnhancedAuthProvider>
        </BrowserRouter>
      </GlobalErrorProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;