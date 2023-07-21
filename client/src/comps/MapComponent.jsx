import React, { useEffect, useRef, useState } from 'react';
import { Layer, Stage } from 'react-konva';

import { useNavigate } from 'react-router';
import { handleKeyDown } from '../util/inputHandler';
import GameMenu from './GameMenu';
import Tile from './Tile';
import BuildingSelectionMenu from './BuildingSelectionMenu';

// Map component
const Map = ({ setLoggedIn }) => {
  const [layerIndex, setLayerIndex] = useState(4);
  const [localMap, setLocalMap] = useState([]);
  const [localCenter, setLocalCenter] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [outposts, setOutposts] = useState([]);
  const [size, setSize] = useState(
    Math.min(window.innerWidth, window.innerHeight) / 20
  );
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [menuOpen, setMenuOpen] = useState(false);
  const [buildingMenuOpen, setBuildingMenuOpen] = useState(false);
  const [buildingId, setBuildingId] = useState(null);

  const stageRef = useRef();

  const stageWidth = window.innerWidth;
  const stageHeight = window.innerHeight;

  const navigate = useNavigate();

  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      setMenuOpen(!menuOpen);
      if (buildingMenuOpen) {
        setBuildingMenuOpen(false);
      }
    }
  };

  const handleResize = () => {
    setSize(Math.min(window.innerWidth, window.innerHeight) / 20);
  };

  const handleLogout = () => {
    fetch('/api/logout', { method: 'POST' }).then((res) => {
      setLoggedIn(false);
      navigate('/login');
    });
  };

  const handleEKey = (e) => {
    if (e.key === 'e' && !menuOpen) {
      setBuildingMenuOpen(!buildingMenuOpen);
    }
  };

  const handleQKey = (e) => {
    if (e.key === 'q') {
      // When 'q' is pressed, increment the layer index and wrap it around if it exceeds 4
      setLayerIndex((layerIndex + 1) % 5);
    }
  };

  useEffect(() => {
    fetch('/api/map')
      .then((res) => {
        if (res.status === 200) {
          return res.json();
        } else {
          navigate('/login');
        }
      })
      .then((data) => {
        setLocalMap(data.map_data);
        setLocalCenter(data.center);
        setBuildings(data.buildings);
        setOutposts(data.outposts);

        const mapCenterIndex = Math.floor(data.map_data.length / 2);
        const initialPos = {
          x: stageWidth / 2 - mapCenterIndex * size,
          y: stageHeight / 2 - mapCenterIndex * size,
        };
        setPos(initialPos);
      });

    window.addEventListener('resize', handleResize);
    window.addEventListener('keydown', handleEscape);
    window.addEventListener('keydown', handleEKey);
    window.addEventListener('keydown', handleQKey);
    window.addEventListener('keydown', (e) =>
      handleKeyDown(e, stageRef.current, size, setPos)
    );

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('keydown', handleEscape);
      window.removeEventListener('keydown', handleEKey);
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keydown', handleQKey);
    };
  }, [layerIndex]);

  return (
    <>
      {localMap.length > 0 ? (
        <>
          <Stage
            ref={stageRef}
            width={stageWidth}
            height={stageHeight}
            position={pos}
            draggable
          >
            <Layer>
              {localMap.map((row, y) =>
                row.map((tile, x) => {
                  const mapCenterIndex = Math.floor(localMap.length / 2);
                  const mapCoord = {
                    x: localCenter[0] + (x - mapCenterIndex),
                    y: localCenter[1] + (y - mapCenterIndex),
                  };
                  const localCoord = { x, y };

                  // Get the buildingId for the current tile
                  const currentBuildingId =
                    buildings[`${mapCoord.x},${mapCoord.y}`];

                  return (
                    <Tile
                      key={`${x},${y},${currentBuildingId}`} // Include buildingId in the key
                      terrain={tile}
                      x={x}
                      y={y}
                      size={size}
                      mapCoord={mapCoord}
                      localCoord={localCoord}
                      selectedBuildingId={buildingId} // Pass buildingId as selectedBuildingId
                      buildings={buildings}
                      setBuildings={setBuildings}
                      layerIndex={layerIndex}
                    />
                  );
                })
              )}
            </Layer>
          </Stage>
          {menuOpen && <GameMenu onLogout={handleLogout} />}
          {buildingMenuOpen && (
            <BuildingSelectionMenu
              setBuildingId={setBuildingId}
              setBuildingMenuOpen={setBuildingMenuOpen}
            />
          )}
        </>
      ) : (
        <div class="flex justify-center items-center h-screen">Loading...</div>
      )}
    </>
  );
};

export default Map;
