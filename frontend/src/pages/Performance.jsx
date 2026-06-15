import {
  BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'

// static data from your training results
const metrics = [
  { name: 'AUC',       LR: 0.9872, XGBoost: 0.9984 },
  { name: 'F1',        LR: 0.9329, XGBoost: 0.9754 },
  { name: 'Precision', LR: 0.9249, XGBoost: 0.9858 },
  { name: 'Recall',    LR: 0.9410, XGBoost: 0.9653 },
]

const featureImportance = [
  { feature: 'velocity_last_30_days',   importance: 0.821 },
  { feature: 'transaction_month',       importance: 0.111 },
  { feature: 'min_amount',              importance: 0.012 },
  { feature: 'recency_frequency_ratio', importance: 0.007 },
  { feature: 'Frequency',               importance: 0.005 },
  { feature: 'reversal_rate',           importance: 0.004 },
  { feature: 'negative_amount_count',   importance: 0.004 },
  { feature: 'std_amount',              importance: 0.004 },
]

export default function Performance() {
  return (
    <div style={{ padding: '20px', flex: 1, background: '#f8f8f8', minHeight: '100vh' }}>

      <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#1a1a1a' }}>
        Model Performance
      </h2>

      {/* metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {[
          { label: 'AUC-ROC',   value: '0.9984', color: '#0F6E56' },
          { label: 'F1 Score',  value: '0.9754', color: '#534AB7' },
          { label: 'Precision', value: '0.9858', color: '#333'    },
          { label: 'Recall',    value: '0.9653', color: '#333'    },
        ].map(m => (
          <div key={m.label} style={{ background: '#fff', borderRadius: '8px', padding: '14px', border: '1px solid #eee' }}>
            <div style={{ fontSize: '11px', color: '#999', marginBottom: '4px' }}>{m.label}</div>
            <div style={{ fontSize: '22px', fontWeight: '600', color: m.color }}>{m.value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>

        {/* model comparison chart */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '16px', border: '1px solid #eee' }}>
          <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: '14px', color: '#333' }}>
            Logistic Regression vs XGBoost
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0.8, 1.05]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="LR"      name="Logistic Regression" fill="#93C5FD" radius={[3,3,0,0]} />
              <Bar dataKey="XGBoost" name="XGBoost"             fill="#534AB7" radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* feature importance chart */}
        <div style={{ background: '#fff', borderRadius: '8px', padding: '16px', border: '1px solid #eee' }}>
          <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: '14px', color: '#333' }}>
            XGBoost Feature Importance
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={featureImportance} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 10 }} />
              <YAxis dataKey="feature" type="category" tick={{ fontSize: 10 }} width={160} />
              <Tooltip />
              <Bar dataKey="importance" fill="#534AB7" radius={[0,3,3,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* badges */}
      <div style={{ marginTop: '16px', background: '#fff', borderRadius: '8px', padding: '16px', border: '1px solid #eee' }}>
        <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: '10px', color: '#333' }}>
          Model Details
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '12px' }}>
          {['Basel II compliant', 'SHAP explanations', 'ADASYN oversampling', 'Stratified split', 'MLflow tracked'].map(b => (
            <span key={b} style={{ fontSize: '11px', padding: '3px 10px', borderRadius: '10px', background: '#EEEDFE', color: '#3C3489' }}>
              {b}
            </span>
          ))}
        </div>
        <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.6' }}>
          <strong>Note:</strong> AUC of 0.9984 reflects the model's ability to separate KMeans-derived proxy labels.
          In production with actual default labels, expected AUC is 0.75–0.85.
          This project demonstrates a complete production-ready ML pipeline.
        </div>
      </div>
    </div>
  )
}
