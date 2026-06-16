import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import PageSkeleton from "../components/PageSkeleton";
import AdminLayout from "./AdminLayout";
import { AdminAuthProvider, useAdminAuth } from "./AuthContext";

const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const AdminArticleList = lazy(() => import("./pages/AdminArticleList"));
const AdminArticleEditor = lazy(() => import("./pages/AdminArticleEditor"));
const AdminLogin = lazy(() => import("./pages/AdminLogin"));

function ProtectedAdmin() {
  const { user, isLoading } = useAdminAuth();
  if (isLoading) return <div className="mx-auto max-w-xl py-20"><PageSkeleton /></div>;
  return user ? <AdminLayout /> : <Navigate to="/admin/login" replace />;
}

function AdminRoutes() {
  const { user } = useAdminAuth();
  return (
    <Suspense fallback={<div className="mx-auto max-w-xl py-20"><PageSkeleton /></div>}>
      <Routes>
        <Route path="login" element={user ? <Navigate to="/admin" replace /> : <AdminLogin />} />
        <Route element={<ProtectedAdmin />}>
          <Route index element={<AdminDashboard />} />
          <Route path="articles" element={<AdminArticleList />} />
          <Route path="articles/new" element={<AdminArticleEditor />} />
          <Route path="articles/:id/edit" element={<AdminArticleEditor />} />
        </Route>
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </Suspense>
  );
}

export default function AdminPage() {
  return <AdminAuthProvider><AdminRoutes /></AdminAuthProvider>;
}
