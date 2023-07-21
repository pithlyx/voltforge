import { useEffect, useState } from 'react';
import { Link, Navigate, Outlet, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css';
import CreateUser from './comps/CreateUser';
import Login from './comps/Login';
import Logout from './comps/Logout';
import Map from './comps/MapComponent';

function App() {
	const [mapData, setMapData] = useState({});
	const [loggedIn, setLoggedIn] = useState(false);

	const getLogin = (navigate) => {
		fetch('/api/login').then((res) => {
			if (res.status === 200) {
				setLoggedIn(true);
			} else {
				setLoggedIn(false);
			}
		});
	};

	useEffect(() => {
		getLogin();
	}, []);

	return (
		<Router>
			<Routes>
				<Route path="/" element={!loggedIn ? <Navigate to={'/game'} /> : <Navigate to={'/login'} />} />
				<Route path="/login" element={<Login loggedIn={loggedIn} setLoggedIn={setLoggedIn} getLogin={getLogin} />} />
				<Route path="/logout" element={<Logout setLoggedIn={setLoggedIn} />} />
				<Route path="/create-user" element={<CreateUser />} />
				<Route path="/game" element={<Map setLoggedIn={setLoggedIn} />} />
				<Route path="/play" element={loggedIn ? <Navigate to="/game" /> : <Navigate to="/login" />} />
			</Routes>
		</Router>
	);
}

export default App;
