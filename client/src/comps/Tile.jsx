import React, { useEffect, useState } from 'react';
import { Rect, Image } from 'react-konva';
import useImage from 'use-image';

const overworldColors = ['darkblue', 'blue', 'yellow', 'green', 'darkgreen'];
const resourceColors = [
  'gray',
  'black',
  'red',
  'blue',
  'darkgreen',
  'yellow',
  'beige',
  'silver',
  'green',
  'gold',
  'purple',
];

// Function to get the image path from the building ID
const getBuildingImagePath = (buildingId) => {
  const tilesPerRow = 10; // The number of tiles per row in the spritesheet
  const tileRow = Math.floor(buildingId / tilesPerRow);
  const tileCol = buildingId % tilesPerRow;

  // Construct the path to the tile image
  const tileImagePath = `tiles/tile_${tileRow}_${tileCol}.png`; // replace with your path

  return tileImagePath;
};

const Tile = ({
  terrain,
  x,
  y,
  size,
  mapCoord,
  localCoord,
  buildings,
  setBuildings,
  selectedBuildingId, // Renamed from buildingId for clarity
  layerIndex,
}) => {
  const [color, setColor] = useState(overworldColors[layerIndex]);
  const [globalPos, setGlobalPos] = useState(mapCoord);
  const [localPos, setLocalPos] = useState(localCoord);
  const [isBuildingPresent, setIsBuildingPresent] = useState(false);

  // Add state for building image
  const [buildingImagePath, setBuildingImagePath] = useState(null);

  // Retrieve the buildingId for the current tile from buildings state
  const buildingId = buildings[`${mapCoord.x},${mapCoord.y}`];

  // Load the image using the useImage hook
  const [buildingImage] = useImage(buildingImagePath);

  useEffect(() => {
    if (layerIndex === 4) {
      setColor(overworldColors[terrain[4]]);
    } else {
      setColor(resourceColors[terrain[layerIndex]]);
    }

    // Update the building image path whenever the buildingId changes
    setBuildingImagePath(getBuildingImagePath(buildingId));
  }, [layerIndex, buildingId]);

  const sendBuildingData = async (x, y, id) => {
    console.log(JSON.stringify({ x, y, id }));
    try {
      const response = await fetch(`/api/buildings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ x, y, id }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data) {
        setBuildings({
          ...buildings,
          [`${globalPos.x},${globalPos.y}`]: selectedBuildingId,
        });
        // Set isBuildingPresent to true
        setIsBuildingPresent(true);
      }
      return data;
    } catch (error) {
      console.error('Error:', error);
      return null;
    }
  };

  const handleTileClick = async () => {
    const currentBuildingId =
      buildings[`${globalPos.x},${globalPos.y}`] || 'None';
    console.log(buildings);
    if (selectedBuildingId === null) {
      // Use selectedBuildingId here
      console.log(
        `Tile info: \nX: ${globalPos.x}\nY: ${globalPos.y}\nBuilding ID: ${currentBuildingId}`
      );
      return;
    }

    console.log(
      `Global:\nX: ${globalPos.x}\nY: ${globalPos.y}\nLocal:\nX: ${localPos.x}\nY: ${localPos.y}`
    );
    console.log('Building ID: ', selectedBuildingId); // Use selectedBuildingId here

    const data = await sendBuildingData(
      globalPos.x,
      globalPos.y,
      selectedBuildingId
    );

    // Only place the building if the server responds OK
    if (data) {
      setBuildings({
        ...buildings,
        [`${globalPos.x},${globalPos.y}`]: selectedBuildingId,
      });
    }
  };

  // Render a different object depending on whether a building is present
  return buildingId === 0 || buildingId || isBuildingPresent ? (
    <Image
      x={x * size}
      y={y * size}
      width={size}
      height={size}
      image={buildingImage}
      onClick={handleTileClick}
    />
  ) : (
    <Rect
      x={x * size}
      y={y * size}
      width={size}
      height={size}
      fill={color}
      onClick={handleTileClick}
    />
  );
};

export default Tile;
