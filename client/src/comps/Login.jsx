import { useState } from 'react';

function Login({ loggedIn, setLoggedIn }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState({});

  const login = async () => {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username: username, password: password }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message); // Throw an error if response is not ok
    }
    return data.user;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (loggedIn) {
      const data = await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }).then((res) => res.json());
      console.log(data);
      setLoggedIn(!loggedIn);
      return;
    }
    const data = await login();
    console.log(data);
    setLoggedIn(!loggedIn);
  };

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={handleLogin}>
        {!loggedIn && (
          <>
            <input
              type="text"
              placeholder="username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              type="password"
              placeholder="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </>
        )}

        <input type="submit" value={loggedIn ? 'Logout' : 'Login'} />
      </form>
      <p>{loggedIn ? 'Logged in' : 'Logged out'}</p>
      {loggedIn && <p>{user.username}</p>}
    </div>
  );
}

export default Login;
