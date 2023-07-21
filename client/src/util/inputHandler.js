export const handleKeyDown = (e, stage, size, setPos) => {
	if (stage) {
		const currentPos = stage.position();

		switch (e.key) {
			case 'w':
				setPos({ x: currentPos.x, y: currentPos.y + size });
				break;
			case 'a':
				setPos({ x: currentPos.x + size, y: currentPos.y });
				break;
			case 's':
				setPos({ x: currentPos.x, y: currentPos.y - size });
				break;
			case 'd':
				setPos({ x: currentPos.x - size, y: currentPos.y });
				break;
			default:
				break;
		}
	}
};
