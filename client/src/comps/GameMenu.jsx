import React from 'react';

const GameMenu = ({ onLogout }) => {
	return (
		<div className="fixed top-0 left-0 w-screen h-screen bg-black bg-opacity-50 flex justify-center items-center">
			<div className="p-5 rounded" style={{ backgroundColor: '#475569' }}>
				<button
					onClick={onLogout}
					className="bg-white text-black px-4 py-2 rounded shadow-lg"
					style={{ backgroundColor: '#94A3B8' }}
				>
					Log Out
				</button>
			</div>
		</div>
	);
};

export default GameMenu;
