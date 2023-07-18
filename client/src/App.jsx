import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css'
import Login from './comps/Login'
import CreateUser from './comps/CreateUser'
import Recovery from './comps/Recovery';

function App() {
  return (
    <Router>
      <div>
        <Link to="/login"><button>Login</button></Link>
        <Link to="/create-user"><button>Create User</button></Link>
        <Link to="/recover"><button>Recover</button></Link>
      </div>

      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/create-user" element={<CreateUser />} />
        <Route path="/recover" element={<Recovery/>} />
      </Routes>
    </Router>
  )
}

export default App
