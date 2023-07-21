import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
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
  const [cityName, setCityName] = useState('');

  const passwordClass =
    passStrength.score > 2 && password === verifyPassword
      ? 'border-green-300 bg-green-100'
      : 'border-red-300 bg-red-100';
  const emailClass =
    email === verifyEmail
      ? 'border-green-300 bg-green-100'
      : 'border-red-300 bg-red-100';

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
        city_name: cityName,
      }),
    });
    const data = await response.json();
    console.log(data);
    if (!response.ok) {
      throw new Error(data.message); // Throw an error if response is not ok
    }

    return data.user;
  };

  const [validationErrors, setValidationErrors] = useState({});

  const handleCreate = async (e) => {
    e.preventDefault();
    let errors = {};

    if (username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    }
    if (password !== verifyPassword) {
      errors.password = 'Passwords do not match';
    }
    if (email !== verifyEmail) {
      errors.email = 'Emails do not match';
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Invalid email';
    }
    if (passStrength.score < 1) {
      errors.password = `Password is not strong enough\n${passStrength.feedback.warning}\n${passStrength.feedback.suggestions}`;
    }
    if (cityName.length < 3) {
      errors.cityName = 'City name must be at least 3 characters';
    }

    setValidationErrors(errors);

    if (Object.keys(errors).length === 0 && userValid) {
      // if there are no errors, create the user
      try {
        const user = await createUser();
        setUser(user);
        window.location.href = '/login'; // Redirect to the login route
      } catch (error) {
        // Display the error message as an alert
        if (error.message.includes('User')) {
          setValidationErrors((prevErrors) => ({
            ...prevErrors,
            username: error.message,
          }));
        }
        if (error.message.includes('Email')) {
          setValidationErrors((prevErrors) => ({
            ...prevErrors,
            email: error.message,
          }));
        }
      }
    }
  };

  const getInputClass = (field) => {
    return validationErrors[field]
      ? 'border-2 border-red-300 bg-red-100 p-2 rounded w-full'
      : 'border-2 border-gray-200 p-2 rounded w-full';
  };

  return (
    <div
      className="flex flex-col items-center p-5 justify-center rounded h-screen w-screen"
      style={{ backgroundColor: '#475569' }}
    >
      <h1 className="text-3xl font-bold mb-4 text-amber-500">Create User</h1>
      <form
        className="p-6 rounded shadow-md"
        style={{ backgroundColor: '#94A3B8' }}
        onSubmit={handleCreate}
      >
        <div className="mb-4">
          <input
            className={getInputClass('username')}
            type="text"
            placeholder="Enter Username"
            name="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          {validationErrors.username && (
            <p className="text-red-500 text-xs mt-1">
              {validationErrors.username}
            </p>
          )}
        </div>

        <div className="flex space-x-4 mb-4">
          <div className="w-1/2">
            <input
              className={getInputClass('password')}
              type="password"
              placeholder="Enter Password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="w-1/2">
            <input
              className={getInputClass('verifyPassword')}
              type="password"
              placeholder="Verify Password"
              name="verifyPassword"
              value={verifyPassword}
              onChange={(e) => setVerifyPassword(e.target.value)}
            />
          </div>
        </div>
        {validationErrors.password && (
          <p className="text-red-500 text-xs mt-1 mb-4">
            {validationErrors.password}
          </p>
        )}

        {/* <p className="mb-4">Password Strength: {passStrength.score}</p> */}

        <div className="flex space-x-4 mb-4">
          <div className="w-1/2">
            <input
              className={getInputClass('email')}
              type="text"
              placeholder="Enter Email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div className="w-1/2">
            <input
              className={getInputClass('verifyEmail')}
              type="text"
              placeholder="Verify Email"
              name="verifyEmail"
              value={verifyEmail}
              onChange={(e) => setVerifyEmail(e.target.value)}
            />
          </div>
        </div>
        {validationErrors.email && (
          <p className="text-red-500 text-xs mt-1 mb-4">
            {validationErrors.email}
          </p>
        )}

        <div className="mb-4">
          <input
            className={getInputClass('cityName')}
            type="text"
            placeholder="City Name"
            name="cityName"
            value={cityName}
            onChange={(e) => setCityName(e.target.value)}
          />
          {validationErrors.cityName && (
            <p className="text-red-500 text-xs mt-1">
              {validationErrors.cityName}
            </p>
          )}
        </div>

        <input
          className="bg-amber-600 text-white p-2 rounded w-full"
          type="submit"
          value="Create User"
        />
      </form>
      <Link to="/login" className="mt-4 underline text-blue-500">
        Go to login
      </Link>
    </div>
  );
}

export default CreateUser;
