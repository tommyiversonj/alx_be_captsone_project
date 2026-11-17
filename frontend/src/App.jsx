import { Navigate, Route, BrowserRouter, Routes } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import NavBar from './components/NavBar'
import RequireAuth from './components/RequireAuth'
import Login from './pages/Login'
import ProductList from './pages/ProductList'
import RecordSale from './pages/RecordSale'
import './App.css'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/products"
            element={
              <RequireAuth>
                <ProductList />
              </RequireAuth>
            }
          />
          <Route
            path="/sales/new"
            element={
              <RequireAuth>
                <RecordSale />
              </RequireAuth>
            }
          />
          <Route path="/" element={<Navigate to="/products" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
