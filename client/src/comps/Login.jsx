import { useState } from "react"


function Login(){
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [loggedIn, setLoggedIn] = useState(false)
    const [user, setUser] = useState({})


    const pingServer = async () => {
        const response = await fetch("/api/")
        return await response.json()
    }

    const handleLogin = async (e) => {
        e.preventDefault()
        const data = await pingServer()
        console.log(data)
        setLoggedIn(!loggedIn)
    }
    
    return (
        <div>
            <h1>Login</h1>
            <form onSubmit={handleLogin}>
                {!loggedIn &&     
                    <>           
                        <input type="text" placeholder="username" name="username" value={username} onChange={(e) => setUsername(e.target.value)} />
                        <input type="password" placeholder="password" name="password" value={password} onChange={(e) => setPassword(e.target.value)} /> 
                    </>
                }

                <input type="submit" value={loggedIn ? "Logout" : "Login"} />
            </form>
            <p>{loggedIn ? "Logged in" : "Logged out"}</p>
            {loggedIn && <p>{user.username}</p>}
        </div>
    )
}

export default Login