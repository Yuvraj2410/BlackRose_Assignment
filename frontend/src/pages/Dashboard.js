import React, {useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";
import '../styles/Dashboard.css'

const Dashboard = () => {
    const [randomNumber, setRandomNumber] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        // Check if token exists in localStorage
        const token = localStorage.getItem('token');
        if(!token) {
            alert('You are nor logged in!');
            navigate('/login') // Redirect to login if no token
        }
    }, [navigate]);

    return (
        <div className="dashboard-container">
            <h1>Dashboard</h1>
            <p>Welcome to the Dashboard!</p>
            <p>Real-time Random Number: <span>{randomNumber || 'Not connected yet'}</span></p>
            {/* WebSocket or other components will go here */}
        </div>
    );
};

export default Dashboard;