import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

export default function NavBar() {
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()

  if (!isAuthenticated) return null

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/products">Products</Link>
      <Link to="/sales/new">Record sale</Link>
      <button onClick={handleLogout}>Log out</button>
    </nav>
  )
}
