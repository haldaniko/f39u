import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import MainLayout from "./layouts/MainLayout";
import PageSkeleton from "./components/PageSkeleton";

const HomePage = lazy(() => import("./pages/HomePage"));
const ArticlePage = lazy(() => import("./pages/ArticlePage"));
const CategoryPage = lazy(() => import("./pages/CategoryPage"));
const SearchPage = lazy(() => import("./pages/SearchPage"));
const AboutPage = lazy(() => import("./pages/AboutPage"));
const ContactPage = lazy(() => import("./pages/ContactPage"));

export default function App() {
  return (
    <MainLayout>
      <Suspense fallback={<PageSkeleton />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/article/:slug" element={<ArticlePage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </MainLayout>
  );
}
