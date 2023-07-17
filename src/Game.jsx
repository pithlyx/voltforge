// Import the necessary modules from React
import React, { useState, useEffect, useRef } from 'react';

// Define the GameObject class
class GameObject {
  constructor(x, y, sprite) {
    this.x = x; // The x-coordinate of the game object
    this.y = y; // The y-coordinate of the game object
    this.sprite = sprite; // The image that represents the game object
  }

  // Define the draw method, which draws the game object on the canvas
  draw(ctx, cameraX, cameraY) {
    // Draw the sprite at the game object's position, offset by the camera position
    ctx.drawImage(this.sprite, this.x * tileSize - cameraX, this.y * tileSize - cameraY, tileSize, tileSize);
  }
}

// Define the IronOre, IronMine, GoldOre, GoldMine, City, and Transporter classes
class IronOre extends GameObject {} // IronOre is a subclass of GameObject
class IronMine extends GameObject {
  constructor(x, y, sprite) {
    super(x, y, sprite); // Call the constructor of the superclass (GameObject)
    this.level = 1; // The level of the mine
    this.rate = 1; // The rate at which the mine produces resources
  }
}
class GoldOre extends GameObject {} // GoldOre is a subclass of GameObject
class GoldMine extends GameObject {
  constructor(x, y, sprite) {
    super(x, y, sprite); // Call the constructor of the superclass (GameObject)
    this.level = 1; // The level of the mine
    this.rate = 1; // The rate at which the mine produces resources
  }
}
class City extends GameObject {
  constructor(x, y, sprite) {
    super(x, y, sprite); // Call the constructor of the superclass (GameObject)
    this.resources = { // The resources that the city has
      iron: 0,
      gold: 0
    };
    this.storage = { // The maximum amount of resources that the city can store
      iron: 100,
      gold: 100
    };
  }

  // Define the collectResources method, which collects resources from nearby mines
  collectResources(gameState) {
    // Loop over all the game objects
    for (const object of gameState.atlasArray.flat()) {
      // If the object is an IronMine or GoldMine and it's close to the city
      if ((object instanceof IronMine || object instanceof GoldMine) && Math.abs(object.x - this.x) <= 1 && Math.abs(object.y - this.y) <= 1) {
        // Increase the city's corresponding resources
        const resource = object instanceof IronMine ? 'iron' : 'gold';
        this.resources[resource] = Math.min(this.resources[resource] + object.rate, this.storage[resource]);
      }
    }
  }
}

class Transporter extends GameObject {
  constructor(x, y, sprite) {
    super(x, y, sprite); // Call the constructor of the superclass (GameObject)
    this.level = 1; // The level of the transporter
    this.range = 1; // The range of the transporter
  }

  // Define the transportResources method, which transports resources from nearby mines to the city
  transportResources(gameState) {
    // Loop over all the game objects
    for (const object of gameState.atlasArray.flat()) {
      // If the object is an IronMine or GoldMine and it's within the transporter's range
      if ((object instanceof IronMine || object instanceof GoldMine) && Math.abs(object.x - this.x) <= this.range && Math.abs(object.y - this.y) <= this.range) {
        // Transport the resources to the city
        const city = gameState.atlasArray.flat().find(obj => obj instanceof City);
        if (city) {
          const resource = object instanceof IronMine ? 'iron' : 'gold';
          city.resources[resource] = Math.min(city.resources[resource] + object.rate, city.storage[resource]);
        }
      }
    }
  }
}

// Define the sprites as new Image objects
const sprites = {
  ironOre: new Image(),
  ironMine: new Image(),
  goldOre: new Image(),
  goldMine: new Image(),
  city: new Image(),
  transporter: new Image()
};
// Set the source of the sprites to the path of the images
sprites.ironOre.src = '/src/assets/tiles/ironOre.png';
sprites.ironMine.src = '/src/assets/tiles/ironMine.png';
sprites.goldOre.src = '/src/assets/tiles/goldOre.png';
sprites.goldMine.src = '/src/assets/tiles/goldMine.png';
sprites.city.src = '/src/assets/tiles/city.png';
sprites.transporter.src = '/src/assets/tiles/transporter.png';

// Define the Game component
function Game() {
  // Create a ref for the canvas element
  const canvasRef = useRef();

  // Initialize the game state using the useState hook
  const [gameState, setGameState] = useState({
    atlasArray: [], // The array that represents the game map
    placingMine: false, // A flag that indicates whether the user is placing a mine
    placingCity: false, // A flag that indicates whether the user is placing a city
    cameraX: 0, // The x-coordinate of the camera position
    cameraY: 0, // The y-coordinate of the camera position
  });

  // Use the useEffect hook to initialize the game when the component mounts
  useEffect(() => {
    // Initialize the atlas array with random game objects
    const atlasArray = createRandomAtlasArray(100, [new IronOre(0, 0, sprites.ironOre), new GoldOre(0, 0, sprites.goldOre), null]);

    // Set the initial game state
    setGameState({ atlasArray, placingMine: false, placingCity: false, cameraX: 0, cameraY: 0 });

    // Get the canvas context
    const ctx = canvasRef.current.getContext('2d');

    // Draw the initial game state
    drawGameState(ctx, gameState, 0, 0);
  }, []);

  // Define the drawGameState function
  function drawGameState(ctx, gameState, cameraX, cameraY) {
    // Clear the canvas
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    // Draw each game object
    for (const object of gameState.atlasArray.flat()) {
      if (object) {
        object.draw(ctx, cameraX, cameraY);
      }
    }
  }

  // Define the handlePlaceMine function
  function handlePlaceMine() {
    setGameState({ ...gameState, placingMine: true });
  }

  // Define the handlePlaceCity function
  function handlePlaceCity() {
    if (!gameState.atlasArray.flat().some(obj => obj instanceof City)) {
      setGameState({ ...gameState, placingCity: true });
    }
  }

  // Define the handleCanvasClick function
  function handleCanvasClick(e) {
    // Calculate the tile coordinates of the click
    const tileX = Math.floor((e.clientX + gameState.cameraX) / tileSize);
    const tileY = Math.floor((e.clientY + gameState.cameraY) / tileSize);

    // If the user is placing a mine, place a mine at the clicked tile
    if (gameState.placingMine) {
      gameState.atlasArray[tileY][tileX] = new IronMine(tileX, tileY, sprites.ironMine);
      setGameState({ ...gameState, placingMine: false });
    }

    // If the user is placing a city, place a city at the clicked tile
    if (gameState.placingCity) {
      gameState.atlasArray[tileY][tileX] = new City(tileX, tileY, sprites.city);
      setGameState({ ...gameState, placingCity: false });
    }
  }

  // Define the handleMouseMove function
  function handleMouseMove(e) {
    // Calculate the tile coordinates of the mouse
    const tileX = Math.floor((e.clientX + gameState.cameraX) / tileSize);
    const tileY = Math.floor((e.clientY + gameState.cameraY) / tileSize);

    // If the user is placing a mine, move the mine to the mouse position
    if (gameState.placingMine) {
      const mine = gameState.atlasArray.flat().find(obj => obj instanceof IronMine);
      if (mine) {
        mine.x = tileX;
        mine.y = tileY;
      }
    }

    // If the user is placing a city, move the city to the mouse position
    if (gameState.placingCity) {
      const city = gameState.atlasArray.flat().find(obj => obj instanceof City);
      if (city) {
        city.x = tileX;
        city.y = tileY;
      }
    }
  }

  // Define the handleKeyDown function
  function handleKeyDown(e) {
    // If the arrow keys are pressed, move the camera
    if (e.key === 'ArrowUp') {
      setGameState({ ...gameState, cameraY: gameState.cameraY - tileSize });
    } else if (e.key === 'ArrowDown') {
      setGameState({ ...gameState, cameraY: gameState.cameraY + tileSize });
    } else if (e.key === 'ArrowLeft') {
      setGameState({ ...gameState, cameraX: gameState.cameraX - tileSize });
    } else if (e.key === 'ArrowRight') {
      setGameState({ ...gameState, cameraX: gameState.cameraX + tileSize });
    }
  }

  // Return the JSX to render
  return (
    <div onKeyDown={handleKeyDown} tabIndex="0">
      <canvas ref={canvasRef} onClick={handleCanvasClick} onMouseMove={handleMouseMove} />
      <button onClick={handlePlaceMine}>Place Mine</button>
      <button onClick={handlePlaceCity} disabled={gameState.atlasArray.flat().some(obj => obj instanceof City)}>Place City</button>
    </div>
  );
}

export default Game;