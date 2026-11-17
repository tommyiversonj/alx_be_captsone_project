import { useEffect, useState } from 'react'
import { api, ApiError } from '../api'

function emptyItem() {
  return { product: '', quantity: 1, unit_price: '' }
}

export default function RecordSale() {
  const [products, setProducts] = useState([])
  const [items, setItems] = useState([emptyItem()])
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api
      .listProducts()
      .then((data) => setProducts(data.results ?? []))
      .catch(() => setError('Failed to load products.'))
  }, [])

  function updateItem(index, field, value) {
    setItems((current) =>
      current.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    )
  }

  function addItem() {
    setItems((current) => [...current, emptyItem()])
  }

  function removeItem(index) {
    setItems((current) => current.filter((_, i) => i !== index))
  }

  function onProductChange(index, productId) {
    const product = products.find((p) => String(p.id) === productId)
    updateItem(index, 'product', productId)
    if (product) updateItem(index, 'unit_price', product.price)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSuccess(null)
    setSubmitting(true)
    try {
      const payload = items.map((item) => ({
        product: Number(item.product),
        quantity: Number(item.quantity),
        unit_price: item.unit_price,
      }))
      const sale = await api.createSale(payload)
      setSuccess(`Sale #${sale.id} recorded.`)
      setItems([emptyItem()])
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to record sale.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <h1>Record a sale</h1>
      <form onSubmit={handleSubmit} className="form">
        {items.map((item, index) => (
          <div className="sale-item-row" key={index}>
            <select
              value={item.product}
              onChange={(e) => onProductChange(index, e.target.value)}
              required
            >
              <option value="" disabled>
                Select product…
              </option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name} ({product.quantity_in_stock} in stock)
                </option>
              ))}
            </select>
            <input
              type="number"
              min="1"
              value={item.quantity}
              onChange={(e) => updateItem(index, 'quantity', e.target.value)}
              placeholder="Quantity"
              required
            />
            <input
              type="number"
              min="0"
              step="0.01"
              value={item.unit_price}
              onChange={(e) => updateItem(index, 'unit_price', e.target.value)}
              placeholder="Unit price"
              required
            />
            {items.length > 1 && (
              <button type="button" onClick={() => removeItem(index)}>
                Remove
              </button>
            )}
          </div>
        ))}
        <button type="button" onClick={addItem}>
          + Add item
        </button>
        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Recording…' : 'Record sale'}
        </button>
      </form>
    </div>
  )
}
