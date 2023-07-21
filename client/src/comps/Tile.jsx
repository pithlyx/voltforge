import React, { useState } from 'react';
import { Rect } from 'react-konva';

const overworldColors = ['darkblue', 'blue', 'yellow', 'green', 'darkgreen'];

const Tile = ({
  terrain,
  x,
  y,
  size,
  mapCoord,
  localCoord,
  buildingId,
  buildings,
  setBuildingId,
  setBuildings,
}) => {
  const color = overworldColors[terrain];
  const [globalPos, setGlobalPos] = useState(mapCoord);
  const [localPos, setLocalPos] = useState(localCoord);

  const handleTileClick = () => {
    const currentBuildingId =
      buildings[`${globalPos.x},${globalPos.y}`] || 'None';

    if (buildingId === null) {
      console.log(
        `Tile info: \nX: ${globalPos.x}\nY: ${globalPos.y}\nBuilding ID: ${currentBuildingId}`
      );
      return;
    }

    console.log(
      `Global:\nX: ${globalPos.x}\nY: ${globalPos.y}\nLocal:\nX: ${localPos.x}\nY: ${localPos.y}`
    );
    console.log('Building ID: ', buildingId);

    setBuildings({
      ...buildings,
      [`${globalPos.x},${globalPos.y}`]: buildingId,
    });
    setBuildingId(null);
  };

  return (
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
