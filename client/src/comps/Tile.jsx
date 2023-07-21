import React, { useState } from 'react';
import { Image as KonvaImage, Rect } from 'react-konva';
import useImage from 'use-image';

const overworldColors = ['darkblue', 'blue', 'yellow', 'green', 'darkgreen'];

const Tile = ({ terrain, x, y, size, mapCoord, localCoord, buildingId, buildings, setBuildingId, setBuildings }) => {
	const color = overworldColors[terrain];
	const [globalPos, setGlobalPos] = useState(mapCoord);
	const [localPos, setLocalPos] = useState(localCoord);

	// Calculate the row and column of the buildingId in the spritesheet
	const buildingRow = Math.floor(buildingId / 10);
	const buildingCol = buildingId % 10;

	// Construct the path to the building image
	const buildingImagePath = `tiles/tile_${buildingRow}_${buildingCol}.png`; // replace with your path

	// Load the building image
	const [buildingImage] = useImage(buildingId !== null ? buildingImagePath : null);

	const handleTileClick = () => {
		// Get the current buildingId of this tile, or set it to 'None' if it doesn't have a building
		const currentBuildingId = buildings[`${globalPos.x},${globalPos.y}`] || 'None';

		// If no building is currently selected, just print out the tile info
		if (buildingId === null) {
			console.log(`Tile info: \nX: ${globalPos.x}\nY: ${globalPos.y}\nBuilding ID: ${currentBuildingId}`);
			return;
		}

		console.log(`Global:\nX: ${globalPos.x}\nY: ${globalPos.y}\nLocal:\nX: ${localPos.x}\nY: ${localPos.y}`);
		console.log('Building ID: ', buildingId);

		// Update the building for this tile in the buildings state
		setBuildings({ ...buildings, [`${globalPos.x},${globalPos.y}`]: buildingId });

		// Set the selected buildingId to null after assigning it to a tile
		setBuildingId(null);
	};

	return (
		<React.Fragment>
			<Rect x={x * size} y={y * size} width={size} height={size} fill={color} onClick={handleTileClick} />
			{buildingId !== null && <KonvaImage image={buildingImage} x={x * size} y={y * size} width={size} height={size} />}
		</React.Fragment>
	);
};

export default Tile;
