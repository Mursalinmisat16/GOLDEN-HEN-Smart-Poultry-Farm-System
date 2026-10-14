import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // <-- for redirect
import Navbar from '../components/Navbar';
import axios from 'axios';
import { FaEye, FaEyeSlash } from 'react-icons/fa';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate(); // <-- initialize router navigation

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:8000/login', {
        email,
        password
      });

      if (res.data === 'incorrect') {
        alert('Wrong credentials!');
      } else {
        console.log('Login success. User ID:', res.data);
        // ✅ Redirect to sensor-data page
        navigate('/sensor-data');
      }
    } catch (error) {
      console.error('Login failed:', error.response?.data || error.message);
      alert('Login request failed. Please try again later.');
    }
  };

  return (
    <>
      <Navbar />

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
        <form 
          onSubmit={handleSubmit}
          className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md"
        >
          <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">Login</h2>

          {/* Email */}
          <div className="mb-4">
            <label htmlFor="email" className="block mb-1 font-medium text-gray-700">Email</label>
            <input 
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
              placeholder="Enter your email"
              required
            />
          </div>

          {/* Password */}
          <div className="mb-4 relative">
            <label htmlFor="password" className="block mb-1 font-medium text-gray-700">Password</label>
            <input 
              type={showPassword ? 'text' : 'password'}
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
              placeholder="Enter your password"
              required
            />
            <div 
              className="absolute right-3 top-9 cursor-pointer text-gray-600 hover:text-black"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <FaEyeSlash /> : <FaEye />}
            </div>
          </div>

          {/* Submit */}
          <button 
            type="submit"
            className="w-full py-2 mt-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold rounded-lg hover:from-purple-500 hover:to-blue-500 transition-all duration-300 cursor-pointer"
          >
            Log In
          </button>
        </form>
      </div>
    </>
  );
}

export default Login;
