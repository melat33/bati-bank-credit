// ShapBars renders the SHAP explanation for one customer
// shap_values comes from POST /predict response
// each item: { feature, impact, direction }

export default function ShapBars({ shapValues }) {
  if (!shapValues || shapValues.length === 0) {
    return <div style={{ color: '#999', fontSize: '12px' }}>No explanation available</div>
  }

  return (
    <div>
      {shapValues.map((item, i) => {
        const isRisk = item.direction === 'increases risk'
        const barColor = isRisk ? '#A32D2D' : '#0F6E56'
        const labelColor = isRisk ? '#791F1F' : '#085041'
        // bar width as percentage of max impact (capped at 100%)
        const maxWidth = Math.min(Math.abs(item.impact) * 30, 100)

        return (
          <div key={i} style={{ marginBottom: '10px' }}>
            {/* feature name and direction */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '3px',
            }}>
              <span style={{ fontSize: '12px', color: '#333' }}>
                {item.feature}
              </span>
              <span style={{ fontSize: '11px', color: labelColor }}>
                {item.direction}
              </span>
            </div>

            {/* bar */}
            <div style={{
              background: '#f0f0f0',
              borderRadius: '2px',
              height: '5px',
            }}>
              <div style={{
                width: `${maxWidth}%`,
                background: barColor,
                height: '5px',
                borderRadius: '2px',
                transition: 'width 0.4s ease',
              }} />
            </div>

            {/* impact value */}
            <div style={{ fontSize: '10px', color: '#999', marginTop: '1px' }}>
              impact: {item.impact > 0 ? '+' : ''}{item.impact.toFixed(3)}
            </div>
          </div>
        )
      })}
    </div>
  )
}
