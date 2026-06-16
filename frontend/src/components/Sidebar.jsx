import { NavLink } from 'react-router-dom'

export default function Sidebar() {
  // NavLink automatically adds 'active' class when route matches
  const linkStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 16px',
    textDecoration: 'none',
    color: '#666',
    fontSize: '13px',
    borderRadius: '6px',
    margin: '2px 8px',
  }

  const activeStyle = {
    background: '#EEEDFE',
    color: '#3C3489',
    fontWeight: '500',
  }

  return (
    <div style={{
      width: '200px',
      minHeight: '100vh',
      background: '#fff',
      borderRight: '1px solid #eee',
      paddingTop: '16px',
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{
        padding: '0 16px 20px',
        fontSize: '14px',
        fontWeight: '600',
        color: '#3C3489',
        borderBottom: '1px solid #eee',
        marginBottom: '8px',
      }}>
        Bati Bank
        <div style={{ fontSize: '11px', color: '#999', fontWeight: '400' }}>
          Credit Risk Platform
        </div>
      </div>

      {/* Nav sections */}
      <div style={{ fontSize: '10px', color: '#999', padding: '8px 16px 4px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        Core Operations
      </div>

      <NavLink to="/" end style={({ isActive }) => ({ ...linkStyle, ...(isActive ? activeStyle : {}) })}>
        Overview
      </NavLink>

      <NavLink to="/batch" style={({ isActive }) => ({ ...linkStyle, ...(isActive ? activeStyle : {}) })}>
        Batch Upload
      </NavLink>

      <NavLink to="/history" style={({ isActive }) => ({ ...linkStyle, ...(isActive ? activeStyle : {}) })}>
        History
      </NavLink>

      <div style={{ fontSize: '10px', color: '#999', padding: '12px 16px 4px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        Analytics
      </div>

      <NavLink to="/performance" style={({ isActive }) => ({ ...linkStyle, ...(isActive ? activeStyle : {}) })}>
        Model Performance
      </NavLink>

      {/* API status */}
      <div style={{
        position: 'fixed',
        bottom: '16px',
        width: '200px',
        padding: '0 16px',
      }}>
        <div style={{
          fontSize: '11px',
          color: '#0F6E56',
          background: '#E1F5EE',
          padding: '6px 10px',
          borderRadius: '6px',
        }}>
          System Online
        </div>
      </div>
    </div>
  )
}