import { useState } from "react"


function Recovery(){
    const [apiKey, setApiKey] = useState("")
    const [email, setemail] = useState("")


    const pingServer = async () => {
        const response = await fetch("/api/")
        return await response.json()
    }

    const handleLogin = async (e) => {
        e.preventDefault()
        const data = await pingServer()
        console.log(data)
    }
    
    return (
        <div>
            <h1>Recover Account</h1>
            <form onSubmit={handleLogin}>
                <input type="text" placeholder="Enter Api-Key" name="apiKey" value={apiKey} onChange={(e) => setApiKey(e.target.value)} />
                <h3>Or</h3>
                <input type="text" placeholder="Enter Email" name="email" value={email} onChange={(e) => setemail(e.target.value)} />
                <br/>
                <input type="submit" value="Recover Account" />
            </form>
        </div>
    )
}

export default Recovery