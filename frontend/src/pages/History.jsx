import { useState, useEffect } from 'react'
import { getAllCustomers } from '../api'

export default function History() {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading]     = useState(true)
  const [filter, setFilter]       = useState('All')
  const [search, setSearch]       = useState('')
  const [error, setError]         = useState(null)

  useEffect(() => {
    getAllCustomers()
      .then(data => {
        setCustomers(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  // filter by risk level and search
  const filtered = customers.filter(c => {
    const matchesFilter = filter === 'All' || c.risk_level === filter
    const matchesSearch = c.customer_id.toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const badgeStyle = (level) => {
    const map = {
      High  : { background: '#FCEBEB', color: '#791F1F' },
      Medium: { background: '#FAEEDA', color: '#633806' },
      Low   : { background: '#E1F5EE', color: '#085041' },
    }
    return {
      ...map[level],
      fontSize: '11px',
      padding: '2px 8px',
      borderRadius: '10px',
      fontWeight: '500',
    }
  }

  return (
    <div style={{ padding: '20px', flex: 1, background: '#f8f8f8', minHeight: '100vh' }}>

      <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '4px', color: '#1a1a1a' }}>
        Customer History
      </h2>
      <p style={{ fontSize: '13px', color: '#999', marginBottom: '20px' }}>
        All scored customers sorted by risk score — {customers.length} total
      </p>

      {/* filters */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '16px', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Search customer ID..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            padding: '7px 12px',
            border: '1px solid #ddd',
            borderRadius: '6px',
            fontSize: '12px',
            width: '200px',
            outline: 'none',
          }}
        />
        {['All', 'High', 'Medium', 'Low'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: '6px 14px',
              border: '1px solid #ddd',
              borderRadius: '6px',
              fontSize: '12px',
              cursor: 'pointer',
              background: filter === f ? '#534AB7' : '#fff',
              color: filter === f ? '#fff' : '#666',
            }}
          >
            {f}
          </button>
        ))}
        <span style={{ fontSize: '12px', color: '#999' }}>
          Showing {filtered.length} customers
        </span>
      </div>

      {error && (
        <div style={{ background: '#FCEBEB', color: '#791F1F', padding: '10px', borderRadius: '6px', marginBottom: '12px', fontSize: '13px' }}>
          {error}
        </div>
      )}

      {/* table */}
      <div style={{ background: '#fff', borderRadius: '8px', border: '1px solid #eee', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
          <thead>
            <tr style={{ background: '#f8f8f8' }}>
              {['Customer ID', 'Risk Score', 'Decision', 'Risk Level'].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', color: '#666', fontWeight: '500', fontSize: '11px', borderBottom: '1px solid #eee' }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} style={{ padding: '20px 16px', color: '#999', textAlign: 'center' }}>
                  Loading customers...
                </td>
              </tr>
            ) : filtered.slice(0, 100).map((c, i) => (
              <tr key={i} style={{ borderTop: '1px solid #f0f0f0' }}>
                <td style={{ padding: '10px 16px', color: '#333', fontWeight: '500' }}>
                  {c.customer_id}
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{
                      width: '60px', height: '4px',
                      background: '#f0f0f0', borderRadius: '2px',
                    }}>
                      <div style={{
                        width: `${Math.round(c.score * 100)}%`,
                        height: '4px',
                        background: c.risk_level === 'High' ? '#A32D2D' : c.risk_level === 'Medium' ? '#854F0B' : '#0F6E56',
                        borderRadius: '2px',
                      }} />
                    </div>
                    <span style={{ color: '#333' }}>{c.score.toFixed(4)}</span>
                  </div>
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <span style={{ color: c.decision === 'Reject' ? '#A32D2D' : '#0F6E56', fontWeight: '500' }}>
                    {c.decision}
                  </span>
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <span style={badgeStyle(c.risk_level)}>{c.risk_level}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filtered.length > 100 && (
          <div style={{ padding: '10px 16px', fontSize: '12px', color: '#999', borderTop: '1px solid #eee' }}>
            Showing first 100 of {filtered.length} results
          </div>
        )}
      </div>
    </div>
  )
}
