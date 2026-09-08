import { useEffect, useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000/api'

function App() {
  const [bills, setBills] = useState([])
  const [amounts, setAmounts] = useState({})
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const fetchBills = async () => {
    try {
      const response = await fetch(`${API_URL}/bills/`)

      if (!response.ok) {
        throw new Error('Failed to fetch bills.')
      }

      const data = await response.json()
      setBills(data)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => {
    fetchBills()
  }, [])

  const handleAmountChange = (billId, value) => {
    setAmounts({
      ...amounts,
      [billId]: value
    })
  }

  const recordPayment = async (billId) => {
    setMessage('')
    setError('')

    const amount = amounts[billId]

    if (!amount) {
      setError('Please enter a payment amount.')
      return
    }

    try {
      const response = await fetch(
        `${API_URL}/bills/${billId}/cash_payment/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            amount: amount
          })
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Payment failed.')
      }

      setMessage('Cash payment recorded successfully.')

      setAmounts({
        ...amounts,
        [billId]: ''
      })

      fetchBills()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="app">
      <h1>Clinic Billing</h1>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      {bills.length === 0 ? (
        <p>No bills found.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Bill</th>
              <th>Patient</th>
              <th>Total</th>
              <th>Paid</th>
              <th>Outstanding</th>
              <th>Cash Payment</th>
            </tr>
          </thead>

          <tbody>
            {bills.map((bill) => (
              <tr key={bill.id}>
                <td>#{bill.id}</td>
                <td>{bill.patient_name}</td>
                <td>KES {Number(bill.total_amount).toFixed(2)}</td>
                <td>KES {Number(bill.total_paid).toFixed(2)}</td>
                <td>KES {Number(bill.balance_due).toFixed(2)}</td>
                <td>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={amounts[bill.id] || ''}
                    onChange={(e) =>
                      handleAmountChange(bill.id, e.target.value)
                    }
                    placeholder="Amount"
                  />

                  <button onClick={() => recordPayment(bill.id)}>
                    Record Payment
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default App