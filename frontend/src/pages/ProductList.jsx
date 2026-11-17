import { useEffect, useState } from 'react'
import { api, ApiError } from '../api'

export default function ProductList() {
  const [products, setProducts] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const data = await api.listProducts()
        if (!cancelled) setProducts(data.results ?? [])
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : 'Failed to load products.')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [])

  if (loading) return <div className="page">Loading products…</div>
  if (error) return <div className="page error">{error}</div>

  return (
    <div className="page">
      <h1>Products</h1>
      {products.length === 0 ? (
        <p>No products yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Price</th>
              <th>In stock</th>
              <th>Low-stock threshold</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => {
              const isLowStock = product.quantity_in_stock <= product.low_stock_threshold
              return (
                <tr key={product.id} className={isLowStock ? 'row-low-stock' : ''}>
                  <td>{product.name}</td>
                  <td>{product.category?.name}</td>
                  <td>{product.price}</td>
                  <td>{product.quantity_in_stock}</td>
                  <td>{product.low_stock_threshold}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </div>
  )
}
