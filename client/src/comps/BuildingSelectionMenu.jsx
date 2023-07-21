import React from 'react';

const BuildingSelectionMenu = ({ setBuildingId, setBuildingMenuOpen }) => {
	// Number of tiles per row in the spritesheet
	const tilesPerRow = 10;

	return (
		<div
			style={{
				position: 'absolute',
				top: '50%',
				left: '50%',
				transform: 'translate(-50%, -50%)',
				display: 'flex',
				justifyContent: 'space-around',
			}}
		>
			{Array(5)
				.fill(0)
				.map((_, index) => {
					// Calculate the row and column of the tile in the spritesheet
					const tileRow = Math.floor(index / tilesPerRow);
					const tileCol = index % tilesPerRow;

					// Construct the path to the tile image
					const tileImagePath = `tiles/tile_${tileRow}_${tileCol}.png`; // replace with your path

					return (
						<div
							key={index}
							style={{ width: '100px', height: '100px' }}
							onClick={() => {
								setBuildingId(index);
								setBuildingMenuOpen(false);
							}}
						>
							<img src={tileImagePath} alt="" style={{ width: '100%', height: '100%' }} />
						</div>
					);
				})}
		</div>
	);
};

export default BuildingSelectionMenu;
