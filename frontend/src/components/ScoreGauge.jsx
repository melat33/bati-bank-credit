import { getRiskColor, getRiskLabel } from '../utils'

// ScoreGauge shows a visual bar for the risk score 0-1
// with a threshold line at 0.5

export default function ScoreGauge({ score }) {
  if (score === undefined || score === null) return null

  const color = getRiskColor(score)
  const label = getRiskLabel(score)
  const percent = Math.round(score * 100)

  const colorMap = {
    red: '#A32D2D',
    orange: '#854F0B',
    green: '#0F6E56',
  }
  const barColor = colorMap[color]

  return (
    <div>
      {/* score number */}
      <div style={{
        fontSize: '28px',
        fontWeight: '600',
        color: barColor,
        marginBottom: '4px',
      }}>
        {score.toFixed(4)}
      </div>

      {/* bar */}
      <div style={{
        background: '#f0f0f0',
        borderRadius: '4px',
        height: '8px',
        position: 'relative',
        marginBottom: '4px',
      }}>
        {/* filled bar */}
        <div style={{
          width: `${percent}%`,
          background: barColor,
          height: '8px',
          borderRadius: '4px',
          transition: 'width 0.4s ease, background 0.4s ease',
        }} />
        {/* threshold line at 50% */}
        <div style={{
          position: 'absolute',
          left: '50%',
          top: '-3px',
          width: '1px',
          height: '14px',
          background: '#ccc',
        }} />
      </div>

      {/* labels */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '10px',
        color: '#999',
      }}>
        <span>0 — safe</span>
        <span>threshold 0.5</span>
        <span>1 — high risk</span>
      </div>

      {/* risk label badge */}
      <div style={{
        display: 'inline-block',
        marginTop: '8px',
        padding: '3px 10px',
        borderRadius: '10px',
        fontSize: '12px',
        fontWeight: '500',
        background: color === 'red' ? '#FCEBEB' : color === 'orange' ? '#FAEEDA' : '#E1F5EE',
        color: barColor,
      }}>
        {label} Risk
      </div>
    </div>
  )
}