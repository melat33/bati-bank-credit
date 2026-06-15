import { useState } from 'react'
import { uploadBatch } from '../api'

export default function BatchUpload() {
  const [file, setFile]         = useState(null)
  const [results, setResults]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setResults(null)
    setError(null)
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await uploadBatch(file)
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!results) return
    const rows = [
      ['customer_id', 'score', 'decision', 'risk_level'],
      ...results.results.map(r => [r.customer_id, r.score, r.decision, r.risk_level])
    ]
    const csv = rows.map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'scored_customers.csv'
    a.click()
  }

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
        Batch Upload
      </h2>
      <p style={{ fontSize: '13px', color: '#999', marginBottom: '20px' }}>
        Upload a CSV of customers and get risk scores for all of them at once.
      </p>

      {/* upload box */}
      <div style={{ background: '#fff', borderRadius: '8px', padding: '20px', border: '1px solid #eee', marginBottom: '16px' }}>
        <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: '12px', color: '#333' }}>
          Select CSV File
        </div>

        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{ fontSize: '13px', marginBottom: '12px', display: 'block' }}
        />

        {file && (
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '12px' }}>
            Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={loading || !file}
          style={{
            padding: '8px 20px',
            background: loading ? '#ccc' : '#534AB7',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '13px',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginRight: '10px',
          }}
        >
          {loading ? 'Scoring...' : 'Score Customers'}
        </button>

        {results && (
          <button
            onClick={handleDownload}
            style={{
              padding: '8px 20px',
              background: '#E1F5EE',
              color: '#085041',
              border: '1px solid #0F6E56',
              borderRadius: '6px',
              fontSize: '13px',
              cursor: 'pointer',
            }}
          >
            Download Results
          </button>
        )}
      </div>

      {/* error */}
      {error && (
        <div style={{ background: '#FCEBEB', color: '#791F1F', padding: '10px', borderRadius: '6px', marginBottom: '12px', fontSize: '13px' }}>
          {error}
        </div>
      )}

      {/* results summary */}
      {results && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
            {[
              { label: 'Total scored',  value: results.total_customers, color: '#534AB7' },
              { label: 'High risk',     value: results.high_risk_count,  color: '#A32D2D' },
              { label: 'Low risk',      value: results.low_risk_count,   color: '#0F6E56' },
            ].map(m => (
              <div key={m.label} style={{ background: '#fff', borderRadius: '8px', padding: '14px', border: '1px solid #eee' }}>
                <div style={{ fontSize: '11px', color: '#999', marginBottom: '4px' }}>{m.label}</div>
                <div style={{ fontSize: '22px', fontWeight: '600', color: m.color }}>{m.value}</div>
              </div>
            ))}
          </div>

          {/* results table */}
          <div style={{ background: '#fff', borderRadius: '8px', border: '1px solid #eee', overflow: 'hidden' }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid #eee', fontSize: '13px', fontWeight: '500', color: '#333' }}>
              Results — top 20 shown
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ background: '#f8f8f8' }}>
                  {['Customer ID', 'Score', 'Decision', 'Risk Level'].map(h => (
                    <th key={h} style={{ padding: '10px 16px', textAlign: 'left', color: '#666', fontWeight: '500', fontSize: '11px' }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.results.slice(0, 20).map((r, i) => (
                  <tr key={i} style={{ borderTop: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '10px 16px', color: '#333' }}>{r.customer_id}</td>
                    <td style={{ padding: '10px 16px', color: '#333' }}>{r.score.toFixed(4)}</td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={{ color: r.decision === 'Reject' ? '#A32D2D' : '#0F6E56', fontWeight: '500' }}>
                        {r.decision}
                      </span>
                    </td>
                    <td style={{ padding: '10px 16px' }}>
                      <span style={badgeStyle(r.risk_level)}>{r.risk_level}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
