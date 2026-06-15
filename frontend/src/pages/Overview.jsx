import { useState, useEffect } from 'react'
import { getAllCustomers, predictCustomer } from '../api'
import ShapBars from '../components/ShapBars'
import ScoreGauge from '../components/ScoreGauge'

export default function Overview() {
  const [customers, setCustomers]   = useState([])
  const [selected, setSelected]     = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState(null)
  const [apiLive, setApiLive]       = useState(false)

  // RFM sliders state
  const [frequency, setFrequency]   = useState(10)
  const [monetary, setMonetary]     = useState(50000)
  const [velocity, setVelocity]     = useState(5)

  // load customers + check API health on mount
  useEffect(() => {
    getAllCustomers()
      .then(data => {
        setCustomers(data)
        setApiLive(true)
      })
      .catch(err => setError(err.message))
  }, [])

  // derived metrics
  const total    = customers.length
  const highRisk = customers.filter(c => c.risk_level === 'High').length
  const approved = customers.filter(c => c.decision === 'Approve').length
  const avgScore = total > 0
    ? (customers.reduce((sum, c) => sum + c.score, 0) / total * 100).toFixed(1)
    : 0
  const approvalRate = total > 0 ? ((approved / total) * 100).toFixed(1) : 0

  // score a customer from the queue
  const handleSelect = async (customer) => {
    setSelected(customer)
    setPrediction(null)
    setLoading(true)
    try {
      const result = await predictCustomer({
        Frequency              : frequency,
        Monetary               : monetary,
        avg_hour               : 14,
        avg_day_of_week        : 2,
        weekend_rate           : 0.1,
        transaction_month      : 11,
        std_amount             : 5000,
        max_amount             : 25000,
        min_amount             : -500,
        log_monetary           : Math.log1p(Math.abs(monetary)),
        reversal_rate          : customer.risk_level === 'High' ? 60 : 10,
        unique_products        : 2,
        unique_providers       : 3,
        avg_daily_transactions : 1.5,
        monetary_per_transaction: monetary / Math.max(frequency, 1),
        negative_amount_count  : 2,
        positive_amount_sum    : monetary,
        velocity_last_30_days  : velocity,
        recency_frequency_ratio: customer.risk_level === 'High' ? 15 : 2,
      })
      setPrediction(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // re-score when sliders change and a customer is selected
  const handleSliderScore = async () => {
    if (!selected) return
    await handleSelect(selected)
  }

  const badgeStyle = (level) => {
    const map = {
      High  : { background: '#FCEBEB', color: '#791F1F' },
      Medium: { background: '#FAEEDA', color: '#633806' },
      Low   : { background: '#E1F5EE', color: '#085041' },
    }
    return { ...map[level], fontSize: '11px', padding: '2px 8px', borderRadius: '10px', fontWeight: '500' }
  }

  const metricCards = [
    {
      label : 'Customers Scored',
      value : total.toLocaleString(),
      trend : '+3,742 total',
      tcolor: '#0F6E56',
      color : '#534AB7',
      icon  : '👥',
    },
    {
      label : 'High Risk Flagged',
      value : highRisk.toLocaleString(),
      trend : `${((highRisk/total)*100).toFixed(1)}% of total`,
      tcolor: '#A32D2D',
      color : '#A32D2D',
      icon  : '⚠️',
    },
    {
      label : 'Approval Rate',
      value : `${approvalRate}%`,
      trend : `${approved.toLocaleString()} approved`,
      tcolor: '#0F6E56',
      color : '#0F6E56',
      icon  : '✅',
    },
    {
      label : 'Model AUC',
      value : '0.9984',
      trend : '+0.0112 vs LR baseline',
      tcolor: '#534AB7',
      color : '#333',
      icon  : '📈',
    },
  ]

  return (
    <div style={{ flex: 1, background: '#f0efe9', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* ── top header bar ── */}
      <div style={{
        background: '#fff',
        borderBottom: '1px solid #e8e8e8',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* left — title + badges */}
        <div>
          <div style={{ fontSize: '13px', fontWeight: '600', color: '#1a1a1a', marginBottom: '2px' }}>
            Overview
          </div>
          <div style={{ display: 'flex', gap: '6px' }}>
            <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '10px', background: '#EEEDFE', color: '#3C3489' }}>
              Basel II compliant
            </span>
            <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '10px', background: '#E1F5EE', color: '#085041' }}>
              Interpretable
            </span>
          </div>
        </div>

        {/* right — API live + run pipeline */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '12px', color: apiLive ? '#0F6E56' : '#999',
            background: apiLive ? '#E1F5EE' : '#f0f0f0',
            padding: '5px 12px', borderRadius: '20px',
          }}>
            <div style={{
              width: '7px', height: '7px', borderRadius: '50%',
              background: apiLive ? '#0F6E56' : '#ccc',
            }} />
            {apiLive ? 'API live' : 'Connecting...'}
          </div>
          <button style={{
            padding: '6px 16px',
            background: '#1a1a2e',
            color: '#fff',
            border: 'none',
            borderRadius: '20px',
            fontSize: '12px',
            cursor: 'pointer',
            fontWeight: '500',
          }}>
            ⚡ Run pipeline
          </button>
        </div>
      </div>

      {/* ── hero tagline ── */}
      <div style={{ padding: '20px 24px 0' }}>
        <div style={{ fontSize: '22px', fontWeight: '700', color: '#1a1a1a', lineHeight: '1.3', marginBottom: '4px' }}>
          Turn behavioral signals into<br />trustworthy credit decisions.
        </div>
        <div style={{ fontSize: '13px', color: '#888', marginBottom: '16px' }}>
          A proxy-target risk model trained on RFM patterns from eCommerce transactions —
          powering BNPL approvals with auditable probability scores.
        </div>
      </div>

      <div style={{ padding: '0 24px 24px' }}>

        {error && (
          <div style={{ background: '#FCEBEB', color: '#791F1F', padding: '10px', borderRadius: '8px', marginBottom: '12px', fontSize: '13px' }}>
            {error}
          </div>
        )}

        {/* ── metric cards ── */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
          {metricCards.map(m => (
            <div key={m.label} style={{
              background: '#fff',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid #eee',
              position: 'relative',
              overflow: 'hidden',
            }}>
              {/* icon blob */}
              <div style={{
                position: 'absolute', right: '12px', top: '12px',
                width: '36px', height: '36px', borderRadius: '10px',
                background: '#f5f4ff',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '16px',
              }}>
                {m.icon}
              </div>
              <div style={{ fontSize: '10px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>
                {m.label}
              </div>
              <div style={{ fontSize: '26px', fontWeight: '700', color: m.color, marginBottom: '4px' }}>
                {m.value}
              </div>
              <div style={{ fontSize: '11px', color: m.tcolor, display: 'flex', alignItems: 'center', gap: '3px' }}>
                <span>↑</span> {m.trend}
              </div>
            </div>
          ))}
        </div>

        {/* ── RFM sliders + two columns ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

          {/* left column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>

            {/* RFM sliders */}
            <div style={{ background: '#fff', borderRadius: '12px', padding: '16px', border: '1px solid #eee' }}>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#1a1a1a', marginBottom: '2px' }}>
                Score a customer
              </div>
              <div style={{ fontSize: '11px', color: '#999', marginBottom: '14px' }}>
                Adjust RFM values then click a customer to score
              </div>

              {/* Frequency slider */}
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '12px', color: '#555' }}>Frequency</span>
                  <span style={{ fontSize: '12px', fontWeight: '600', color: '#534AB7' }}>
                    {frequency} txns / 90 days
                  </span>
                </div>
                <input
                  type="range" min="1" max="100" value={frequency}
                  onChange={e => setFrequency(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#534AB7' }}
                />
              </div>

              {/* Monetary slider */}
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '12px', color: '#555' }}>Monetary</span>
                  <span style={{ fontSize: '12px', fontWeight: '600', color: '#534AB7' }}>
                    {monetary.toLocaleString()} UGX avg / month
                  </span>
                </div>
                <input
                  type="range" min="1000" max="500000" step="1000" value={monetary}
                  onChange={e => setMonetary(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#534AB7' }}
                />
              </div>

              {/* Velocity slider */}
              <div style={{ marginBottom: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '12px', color: '#555' }}>Velocity (last 30 days)</span>
                  <span style={{ fontSize: '12px', fontWeight: '600', color: '#534AB7' }}>
                    {velocity} txns
                  </span>
                </div>
                <input
                  type="range" min="0" max="50" value={velocity}
                  onChange={e => setVelocity(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#534AB7' }}
                />
              </div>

              <button
                onClick={handleSliderScore}
                disabled={!selected || loading}
                style={{
                  width: '100%',
                  padding: '9px',
                  background: !selected ? '#ccc' : '#1a1a2e',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '13px',
                  fontWeight: '500',
                  cursor: !selected ? 'not-allowed' : 'pointer',
                }}
              >
                {loading ? 'Scoring...' : '⚡ Submit decision'}
              </button>
            </div>

            {/* customer queue */}
            <div style={{ background: '#fff', borderRadius: '12px', padding: '16px', border: '1px solid #eee' }}>
              <div style={{ fontSize: '13px', fontWeight: '600', color: '#1a1a1a', marginBottom: '2px' }}>
                Recent applicants
              </div>
              <div style={{ fontSize: '11px', color: '#999', marginBottom: '12px' }}>
                Top {Math.min(customers.length, 8)} by risk score from /customers endpoint
              </div>

              {customers.length === 0 ? (
                <div style={{ color: '#999', fontSize: '13px' }}>Loading customers...</div>
              ) : (
                <>
                  {/* table header */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 80px 60px 70px', gap: '8px', padding: '0 4px 6px', borderBottom: '1px solid #f0f0f0' }}>
                    {['Customer', 'Score', 'Risk %', 'Decision'].map(h => (
                      <div key={h} style={{ fontSize: '10px', color: '#999', fontWeight: '500', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        {h}
                      </div>
                    ))}
                  </div>

                  {customers.slice(0, 8).map(c => (
                    <div
                      key={c.customer_id}
                      onClick={() => handleSelect(c)}
                      style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 80px 60px 70px',
                        gap: '8px',
                        padding: '9px 4px',
                        borderBottom: '1px solid #f8f8f8',
                        cursor: 'pointer',
                        borderRadius: '6px',
                        background: selected?.customer_id === c.customer_id ? '#f5f4ff' : 'transparent',
                        alignItems: 'center',
                      }}
                    >
                      <div style={{ fontSize: '12px', fontWeight: '500', color: '#1a1a1a' }}>
                        {c.customer_id.replace('CustomerId_', 'C-')}
                      </div>
                      <div style={{ fontSize: '12px', color: '#555' }}>
                        {Math.round(c.score * 1000)}
                      </div>
                      <div style={{
                        fontSize: '12px', fontWeight: '500',
                        color: c.risk_level === 'High' ? '#A32D2D' : c.risk_level === 'Medium' ? '#854F0B' : '#0F6E56',
                      }}>
                        {(c.score * 100).toFixed(0)}%
                      </div>
                      <span style={badgeStyle(c.risk_level)}>{c.decision}</span>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>

          {/* right column — prediction panel */}
          <div style={{ background: '#fff', borderRadius: '12px', padding: '16px', border: '1px solid #eee' }}>
            <div style={{ fontSize: '13px', fontWeight: '600', color: '#1a1a1a', marginBottom: '2px' }}>
              AI Prediction
            </div>
            <div style={{ fontSize: '11px', color: '#999', marginBottom: '14px' }}>
              {selected ? selected.customer_id : 'Select a customer from the queue'}
            </div>

            {!selected && !loading && (
              <div style={{
                display: 'flex', flexDirection: 'column', alignItems: 'center',
                justifyContent: 'center', height: '300px', color: '#ccc',
              }}>
                <div style={{ fontSize: '40px', marginBottom: '10px' }}>👆</div>
                <div style={{ fontSize: '13px' }}>Click any customer to score</div>
              </div>
            )}

            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '300px', color: '#534AB7', fontSize: '13px' }}>
                Computing prediction...
              </div>
            )}

            {prediction && !loading && (
              <div>
                {/* default probability — large like Lovable */}
                <div style={{
                  background: '#f8f8f8', borderRadius: '10px',
                  padding: '16px', marginBottom: '14px', textAlign: 'center',
                }}>
                  <div style={{ fontSize: '10px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' }}>
                    Default Probability
                  </div>
                  <div style={{ fontSize: '42px', fontWeight: '700', color: prediction.score >= 0.7 ? '#A32D2D' : prediction.score >= 0.4 ? '#854F0B' : '#0F6E56' }}>
                    {(prediction.score * 100).toFixed(1)}
                    <span style={{ fontSize: '20px', fontWeight: '400' }}>%</span>
                  </div>
                  {/* colored gradient bar */}
                  <div style={{
                    height: '6px', borderRadius: '3px', marginTop: '8px',
                    background: 'linear-gradient(to right, #0F6E56, #f0c040, #A32D2D)',
                    position: 'relative',
                  }}>
                    <div style={{
                      position: 'absolute',
                      left: `${prediction.score * 100}%`,
                      top: '-4px',
                      width: '14px', height: '14px',
                      borderRadius: '50%',
                      background: '#1a1a2e',
                      border: '2px solid #fff',
                      transform: 'translateX(-50%)',
                      boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
                    }} />
                  </div>
                </div>

                {/* credit score + decision + suggested loan */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '14px' }}>
                  <div style={{ background: '#f8f8f8', borderRadius: '8px', padding: '10px' }}>
                    <div style={{ fontSize: '10px', color: '#999', marginBottom: '3px' }}>Credit score</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#1a1a1a' }}>
                      {Math.round((1 - prediction.score) * 850)}
                    </div>
                  </div>
                  <div style={{ background: '#f8f8f8', borderRadius: '8px', padding: '10px' }}>
                    <div style={{ fontSize: '10px', color: '#999', marginBottom: '3px' }}>Decision</div>
                    <span style={{
                      fontSize: '12px', fontWeight: '600', padding: '3px 8px',
                      borderRadius: '6px',
                      background: prediction.decision === 'Reject' ? '#FCEBEB' : '#E1F5EE',
                      color: prediction.decision === 'Reject' ? '#791F1F' : '#085041',
                    }}>
                      {prediction.decision}
                    </span>
                  </div>
                  <div style={{ background: '#f8f8f8', borderRadius: '8px', padding: '10px' }}>
                    <div style={{ fontSize: '10px', color: '#999', marginBottom: '3px' }}>Suggested loan</div>
                    <div style={{ fontSize: '13px', fontWeight: '700', color: '#1a1a1a' }}>
                      {prediction.decision === 'Approve'
                        ? `${(monetary * 0.3).toLocaleString()} UGX`
                        : '—'}
                    </div>
                  </div>
                </div>

                {/* SHAP explanation */}
                <div style={{ fontSize: '11px', fontWeight: '600', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                  Why this score
                </div>
                <ShapBars shapValues={prediction.shap_values} />

                {/* action buttons */}
                <div style={{ display: 'flex', gap: '8px', marginTop: '14px' }}>
                  <button style={{ flex: 1, padding: '9px', fontSize: '12px', fontWeight: '500', background: '#E1F5EE', color: '#085041', border: '1px solid #0F6E56', borderRadius: '8px', cursor: 'pointer' }}>
                    Approve
                  </button>
                  <button style={{ flex: 1, padding: '9px', fontSize: '12px', fontWeight: '500', background: '#fff8f0', color: '#633806', border: '1px solid #854F0B', borderRadius: '8px', cursor: 'pointer' }}>
                    Review
                  </button>
                  <button style={{ flex: 1, padding: '9px', fontSize: '12px', fontWeight: '500', background: '#FCEBEB', color: '#791F1F', border: '1px solid #A32D2D', borderRadius: '8px', cursor: 'pointer' }}>
                    Reject
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}