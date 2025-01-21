import React, {useState} from "react";
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import '../styles/LoginPage.css'


function Login(){
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try{
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post('http://127.0.0.1:8000/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            }) ;
            const token = response.data.token;
            localStorage.setItem('token', token); // Save the token for session persistence
            setLoading(false);
            navigate('/dashboard'); // Redirect to Dashboard
        } catch (err){
            setLoading(false);
            setError('Invalid username or password');
        }
    };

    return (
        <div className="login-container">
            <h1>Login</h1>
            <form onSubmit={handleLogin}>
                <input 
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                />
                <input 
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Logging in...' : 'Login'}
                </button>
            </form>
            {error && <p style={{color : 'red'}}>{error}</p>}
        </div>
    );
}

export default Login;