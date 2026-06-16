import { useState, useEffect } from 'react'
import { getAllCustomers, predictCustomer } from '../api'
import ShapBars from '../components/ShapBars'
import ScoreGauge from '../components/ScoreGauge'

export default function Overview() {
  // ─── state ───────────────────────────────────────────
  const [customers, setCustomers]     = useState([])
  const [selected, setSelected]       = useState(null)
  const [prediction, setPrediction]   = useState(null)
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)

  // ─── load customers on mount ─────────────────────────
  useEffect(() => {
    getAllCustomers()
      .then(data => setCustomers(data))
      .catch(err => setError(err.message))
  }, [])

  // ─── metrics derived from customers ──────────────────
  const total     = customers.length
  const highRisk  = customers.filter(c => c.risk_level === 'High').length
  const approved  = customers.filter(c => c.decision === 'Approve').length
  const avgScore  = total > 0
    ? (customers.reduce((sum, c) => sum + c.score, 0) / total).toFixed(3)
    : 0

  // ─── handle customer click ────────────────────────────
  const handleSelect = async (customer) => {
    setSelected(customer)
    setPrediction(null)
    setLoading(true)
    try {
      // build a minimal feature dict from what we have
      // in a real app the customer row would include all features
      const result = await predictCustomer({
        Frequency             : 5,
        Monetary              : customer.score * 100000,
        avg_hour              : 14,
        avg_day_of_week       : 2,
        weekend_rate          : 0.1,
        transaction_month     : 11,
        std_amount            : 5000,
        max_amount            : 25000,
        min_amount            : -500,
        log_monetary          : 9.9,
        reversal_rate         : customer.risk_level === 'High' ? 60 : 10,
        unique_products       : 2,
        unique_providers      : 3,
        avg_daily_transactions: 1.5,
        monetary_per_transaction: 4000,
        negative_amount_count : 2,
        positive_amount_sum   : 25000,
        velocity_last_30_days : customer.risk_level === 'High' ? 0 : 10,
        recency_frequency_ratio: customer.risk_level === 'High' ? 15 : 2,
      })
      setPrediction(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // ─── risk badge style ─────────────────────────────────
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

  // ─── render ───────────────────────────────────────────
  return (
    <div style={{ padding: '20px', flex: 1, background: '#f8f8f8', minHeight: '100vh' }}>

      <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#1a1a1a' }}>
        Overview
      </h2>

      {error && (
        <div style={{ background: '#FCEBEB', color: '#791F1F', padding: '10px', borderRadius: '6px', marginBottom: '12px', fontSize: '13px' }}>
          {error}
        </div>
      )}

      {/* ── metric cards ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {[
          { label: 'Total customers', value: total,              color: '#534AB7' },
          { label: 'High risk',       value: highRisk,           color: '#A32D2D' },
          { label: 'Approved',        value: approved,           color: '#0F6E56' },
          { label: 'Avg risk score',  value: avgScore,           color: '#333'    },
        ].map(m => (
          <div key={m.label} style={{ background: '#fff', borderRadius: '8px', padding: '14px', border: '1px solid #eee' }}>
            <div style={{ fontSize: '11px', color: '#999', marginBottom: '4px' }}>{m.label}</div>
            <div style={{ fontSize: '22px', fontWeight: '600', color: m.color }}>{m.value}</div>
          </div>
        ))}
      </div>

      {/* ── two columns ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

        {/* left — customer queue */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '14px', border: '1px solid #eee' }}>
          <div style={{ fontSize: '11px', fontWeight: '500', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
            Customer Queue — click to score
          </div>

          {customers.length === 0 ? (
            <div style={{ color: '#999', fontSize: '13px' }}>Loading customers...</div>
          ) : (
            customers.slice(0, 10).map(c => (
              <div
                key={c.customer_id}
                onClick={() => handleSelect(c)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '8px',
                  borderBottom: '1px solid #f0f0f0',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  background: selected?.customer_id === c.customer_id ? '#f5f4ff' : 'transparent',
                }}
              >
                {/* avatar */}
                <div style={{
                  width: '28px', height: '28px', borderRadius: '50%',
                  background: c.risk_level === 'High' ? '#FCEBEB' : '#E1F5EE',
                  color: c.risk_level === 'High' ? '#791F1F' : '#085041',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '10px', fontWeight: '500', flexShrink: 0,
                }}>
                  {c.customer_id.slice(-2)}
                </div>

                {/* name */}
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '12px', fontWeight: '500', color: '#333' }}>{c.customer_id}</div>
                  <div style={{ fontSize: '11px', color: '#999' }}>score: {c.score}</div>
                </div>

                {/* badge */}
                <span style={badgeStyle(c.risk_level)}>{c.risk_level}</span>
              </div>
            ))
          )}
        </div>

        {/* right — prediction panel */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '14px', border: '1px solid #eee' }}>
          <div style={{ fontSize: '11px', fontWeight: '500', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>
            AI Prediction — {selected ? selected.customer_id : 'select a customer'}
          </div>

          {!selected && (
            <div style={{ color: '#999', fontSize: '13px' }}>
              Click any customer in the queue to see their risk prediction and SHAP explanation.
            </div>
          )}

          {loading && (
            <div style={{ color: '#534AB7', fontSize: '13px' }}>Computing prediction...</div>
          )}

          {prediction && !loading && (
            <div>
              {/* score gauge */}
              <div style={{ marginBottom: '16px' }}>
                <ScoreGauge score={prediction.score} />
              </div>

              {/* decision */}
              <div style={{
                display: 'flex',
                gap: '10px',
                marginBottom: '16px',
              }}>
                <div style={{ flex: 1, background: '#f8f8f8', borderRadius: '6px', padding: '10px', textAlign: 'center' }}>
                  <div style={{ fontSize: '11px', color: '#999', marginBottom: '3px' }}>Decision</div>
                  <div style={{
                    fontSize: '15px', fontWeight: '600',
                    color: prediction.decision === 'Reject' ? '#A32D2D' : '#0F6E56',
                  }}>
                    {prediction.decision}
                  </div>
                </div>
                <div style={{ flex: 1, background: '#f8f8f8', borderRadius: '6px', padding: '10px', textAlign: 'center' }}>
                  <div style={{ fontSize: '11px', color: '#999', marginBottom: '3px' }}>Model</div>
                  <div style={{ fontSize: '13px', fontWeight: '500', color: '#333' }}>XGBoost</div>
                </div>
              </div>

              {/* SHAP explanation */}
              <div style={{ fontSize: '11px', fontWeight: '500', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Why this score
              </div>
              <ShapBars shapValues={prediction.shap_values} />

              {/* action buttons */}
              <div style={{ display: 'flex', gap: '8px', marginTop: '14px' }}>
                <button style={{ flex: 1, padding: '8px', fontSize: '12px', background: '#E1F5EE', color: '#085041', border: '1px solid #0F6E56', borderRadius: '6px', cursor: 'pointer' }}>
                  Approve
                </button>
                <button style={{ flex: 1, padding: '8px', fontSize: '12px', background: '#fff8f0', color: '#633806', border: '1px solid #854F0B', borderRadius: '6px', cursor: 'pointer' }}>
                  Review
                </button>
                <button style={{ flex: 1, padding: '8px', fontSize: '12px', background: '#FCEBEB', color: '#791F1F', border: '1px solid #A32D2D', borderRadius: '6px', cursor: 'pointer' }}>
                  Reject
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
