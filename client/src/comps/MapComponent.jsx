import React, { useState, useEffect } from 'react';
import { Stage, Layer, Rect } from 'react-konva';

const resources = ['blue', 'yellow', 'green', 'darkgreen'];

const MapComponent = ({
  center,
  mapData,
  updateMapData,
  loggedIn,
  setLoggedIn,
}) => {
  const [position, setPosition] = useState({
    x: mapData.x,
    y: mapData.y,
  });
  const [tileSize, setTileSize] = useState(128);

  useEffect(() => {
    const viewportMin = Math.min(window.innerWidth, window.innerHeight);
    setTileSize(viewportMin / 10);
  }, []);

  console.log(mapData);

  const gameMap = mapData.map_data;

  const handleLogout = async () => {
    const data = await fetch('/api/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }).then((res) => res.json());
    console.log(data);
    logout();
  };

  if (mapData.map_data) {
    return (
      <>
        <button
          style={{ position: 'absolute', top: 20, left: 20 }}
          onClick={handleLogout}
        >
          Logout
        </button>
        <Stage
          width={gameMap[0].length * tileSize}
          height={gameMap.length * tileSize}
        >
          <Layer>
            {gameMap.map((row, y) =>
              row.map((tile, x) => {
                const color = resources[tile[0]];
                return (
                  <Rect
                    key={`${x}-${y}`}
                    x={x * tileSize}
                    y={y * tileSize}
                    width={tileSize}
                    height={tileSize}
                    fill={color}
                  />
                );
              })
            )}
          </Layer>
        </Stage>
      </>
    );
  } else {
    return <div>Loading...</div>;
  }
};

export default MapComponent;
