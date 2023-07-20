import { useEffect, useState } from 'react';
import zxcvbn from 'zxcvbn'; // import the library

function CreateUser() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [verifyPassword, setVerifyPassword] = useState('');
  const [passStrength, setPassStrength] = useState(zxcvbn('pass')); // 0-4, 0 is weak, 4 is strong
  const [email, setEmail] = useState('');
  const [verifyEmail, setVerifyEmail] = useState('');
  const [userValid, setUserValid] = useState(false);
  const [user, setUser] = useState({});

  useEffect(() => {
    setPassStrength(zxcvbn(password));
  }, [password]);

  useEffect(() => {
    if (
      username.length > 3 &&
      passStrength.score >= 0 &&
      email &&
      email === verifyEmail &&
      password === verifyPassword
    ) {
      setUserValid(true);
    } else {
      setUserValid(false);
    }
    console.log(userValid);
  }, [
    username,
    password,
    verifyPassword,
    email,
    verifyEmail,
    passStrength,
    userValid,
  ]);

  const createUser = async () => {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        password: password,
        email: email,
      }),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message); // Throw an error if response is not ok
    }

    return data.user;
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (username.length < 3) {
      return alert('Username must be at least 3 characters');
    } else if (password !== verifyPassword) {
      return alert('Passwords do not match');
    } else if (email !== verifyEmail) {
      return alert('Emails do not match');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return alert('Invalid email');
    } else if (passStrength.score < 1) {
      return alert(
        `Password is not strong enough\n${passStrength.feedback.warning}\n${passStrength.feedback.suggestions}`
      );
    }
    if (userValid) {
      try {
        const user = await createUser();
        setUser(user);
        window.location.href = '/login'; // Redirect to the login route
      } catch (error) {
        alert(error.message); // Display the error message as an alert
      }
    }
  };

  return (
    <div>
      <h1>Create User</h1>
      <form onSubmit={handleCreate}>
        <input
          type="text"
          placeholder="Enter Username"
          name="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <br />
        <input
          type="password"
          placeholder="Enter Password"
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          type="password"
          placeholder="Verify Password"
          name="verifyPassword"
          value={verifyPassword}
          onChange={(e) => setVerifyPassword(e.target.value)}
        />
        <br />
        Password Strength: {passStrength.score}
        <br />
        <input
          type="text"
          placeholder="Enter Email"
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="text"
          placeholder="Verify Email"
          name="verifyEmail"
          value={verifyEmail}
          onChange={(e) => setVerifyEmail(e.target.value)}
        />
        <br />
        <input type="submit" value="Create User" />
      </form>
    </div>
  );
}

export default CreateUser;
