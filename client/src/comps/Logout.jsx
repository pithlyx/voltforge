import { useEffect } from 'react';

const Logout = ({ setLoggedIn }) => {
	useEffect(() => {
		const logout = async () => {
			const response = await fetch('/api/logout', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
			});
			if (response.ok) {
				setLoggedIn(false);
			}
		};
		logout();
	}, []);

	return <div>Logging out...</div>;
};

export default Logout;
