import { useEffect, useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  Navigate,
} from 'react-router-dom';
import './App.css';
import Login from './comps/Login';
import CreateUser from './comps/CreateUser';
import Recovery from './comps/Recovery';
import MapComponent from './comps/MapComponent';

function App() {
  const [mapData, setMapData] = useState({});
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    fetch('/api/login').then((res) => {
      if (res.status === 200) {
        setLoggedIn(true);
        console.log('logged in');
      }
    });
  }, []);

  const getData = useEffect(() => {
    fetch('/api/map')
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setMapData(data);
      });
  }, []);

  return (
    <Router>
      <div>
        {loggedIn ? (
          <Navigate to="/game" />
        ) : (
          <>
            <Link to="/login">
              <button>Login</button>
            </Link>
            <Link to="/create-user">
              <button>Create User</button>
            </Link>
            <Link to="/recover">
              <button>Recover</button>
            </Link>
          </>
        )}
      </div>

      <Routes>
        <Route
          path="/"
          element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
        />
        <Route
          path="/login"
          element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} />}
        />
        <Route path="/create-user" element={<CreateUser />} />
        <Route
          path="/game"
          element={
            <MapComponent
              mapData={mapData}
              updateMap={setMapData}
              loggedIn={loggedIn}
              setLoggedIn={setLoggedIn}
            />
          }
        />

        <Route path="/recover" element={<Recovery />} />
      </Routes>
    </Router>
  );
}

export default App;
