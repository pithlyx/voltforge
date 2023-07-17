const { GameObject, Resource, Mine, IronOre, GoldOre, IronMine, GoldMine } = require('./gameObjects');

describe('GameObject', () => {
  test('should correctly instantiate a game object', () => {
    const gameObject = new GameObject(1, 2, 'sprite.png');
    expect(gameObject.x).toBe(1);
    expect(gameObject.y).toBe(2);
    expect(gameObject.sprite).toBe('sprite.png');
  });
});

