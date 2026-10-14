import { Link, useNavigate } from 'react-router-dom';

function Navbar() {
  const navigate = useNavigate();

  return (
    <nav style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 20px', background: '#eee' }}>
      <div style={{ display: 'flex', gap: '15px' }}>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/contact">Contact Us</Link>
      </div>
      <button onClick={() => navigate('/login')}>Login</button>
    </nav>
  );
}

export default Navbar;