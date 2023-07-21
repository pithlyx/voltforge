import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Login({ loggedIn, setLoggedIn }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState({});
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  const login = async () => {
    if (loggedIn) {
      throw new Error('Already logged in');
    }
    fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username: username, password: password }),
    })
      .then((response) => {
        if (response.ok) {
          setLoggedIn(true);
          navigate('/game'); // Add this line
          return response.json();
        }
        throw new Error(response.statusText);
      })
      .then((data) => {
        console.log(data);
      });
  };

  const logout = async () => {
    const response = await fetch('/api/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (response.ok) {
      setLoggedIn(false);
      setUser({});
      return response.json();
    } else {
      throw new Error('Logout failed.');
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);

    if (loggedIn) {
      try {
        await logout();
        setLoggedIn(false);
        navigate('/login');
      } catch (err) {
        setError(err.message);
      }
    } else {
      try {
        const response = await login();
        if (response && response.status === 200) {
          console.log(response.json());
          setLoggedIn(true);
          navigate('/game');
        } else {
          setError('Invalid credentials. Please try again.');
        }
      } catch (err) {
        setError('An error occurred. Please try again.');
      }
    }
  };

  const getInputClass = () => {
    return error
      ? 'border-2 border-red-300 bg-red-100 p-2 rounded w-full mb-4'
      : 'border-2 border-gray-200 p-2 rounded w-full mb-4';
  };

  return (
    <div
      className="flex flex-col items-center justify-center h-screen w-screen"
      style={{ backgroundColor: '#475569' }}
    >
      <h1 className="text-3xl font-bold mb-4 text-orange-600">Login</h1>
      <form
        className="bg-white p-6 rounded shadow-md"
        onSubmit={handleLogin}
        style={{ backgroundColor: '#94A3B8' }}
      >
        {!loggedIn && (
          <>
            <input
              className={getInputClass()}
              type="text"
              placeholder="username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              className={getInputClass()}
              type="password"
              placeholder="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
          </>
        )}

        <input
          className="bg-blue-500 text-white p-2 rounded w-full"
          type="submit"
          value={loggedIn ? 'Logout' : 'Login'}
        />
        {loggedIn && (
          <button
            className="bg-blue-500 text-white p-2 rounded w-full"
            type="button"
            onClick={() => navigate('/game')}
          >
            Play Game
          </button>
        )}
      </form>
      <Link to="/create-user" className="mt-4 underline text-blue-500">
        Create an account
      </Link>
    </div>
  );
}

export default Login;
