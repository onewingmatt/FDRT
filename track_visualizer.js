// Enhanced Monaco Track Visualization
// Draw lane boundaries, corner zones, and track sections

class TrackVisualizer {
    constructor(canvas, ctx, trackData) {
        this.canvas = canvas;
        this.ctx = ctx;
        this.trackData = trackData;
        
        // Calculate scale to fit track on canvas
        const trackWidth = 414; // Approx track coordinate width
        const trackHeight = 708; // Approx track coordinate height
        this.scale = Math.min(canvas.width / trackWidth, canvas.height / trackHeight) * 0.9;
        
        // Center the track on canvas
        this.offsetX = (canvas.width - trackWidth * this.scale) / 2;
        this.offsetY = (canvas.height - trackHeight * this.scale) / 2;
        
        console.log(`Scale: ${this.scale}, Offset: (${this.offsetX}, ${this.offsetY})`);
    }

    clear() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    drawLaneBoundaries() {
        this.ctx.strokeStyle = 'rgba(255, 255, 0, 0.5)';
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);

        // Draw lane boundaries by section
        let prevX = null, prevY = null;
        
        this.trackData.spaces.forEach((space, idx) => {
            if (space.id === 0 || idx === this.trackData.spaces.length - 1) {
                // Start of track section
                if (prevX !== null) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(prevX, prevY);
                    this.ctx.lineTo(space.x, space.y);
                    this.ctx.stroke();
                }
                prevX = space.x;
                prevY = space.y;
            }
        });
        this.ctx.setLineDash([]); // Reset line dash
    }

    drawCornerZones() {
        // Highlight corner zones with colored overlays
        const cornerColors = {
            'sainte_devote': 'rgba(0, 100, 255, 0.2)',    // Blue
            'masgenet': 'rgba(255, 255, 0, 0.2)',      // Yellow  
            'hairpin': 'rgba(255, 0, 0, 0.2)',        // Red
            'portier': 'rgba(0, 255, 0, 0.2)',        // Green
            'pool': 'rgba(255, 165, 0, 0.2)',         // Orange
            'rascasse': 'rgba(128, 0, 255, 0.2)',       // Purple
            'noghes': 'rgba(0, 255, 255, 0.2)'        // Cyan
        };

        // Draw corner zone highlights
        this.trackData.spaces.forEach(space => {
            if (space.corner_zone && cornerColors[space.corner_zone]) {
                const nextSpace = this.trackData.spaces.find(s => s.id === space.id + 1);
                if (nextSpace) {
                    // Highlight corner area between spaces
                    this.ctx.fillStyle = cornerColors[space.corner_zone];
                    this.ctx.globalAlpha = 0.3;
                    
                    // Draw corner zone overlay
                    this.ctx.beginPath();
                    this.ctx.moveTo(space.x, space.y);
                    this.ctx.lineTo(nextSpace.x, nextSpace.y);
                    this.ctx.lineTo(nextSpace.x, nextSpace.y - 20);  // Go up for corner
                    this.ctx.lineTo(space.x, space.y - 20);
                    this.ctx.closePath();
                    this.ctx.fill();
                    
                    this.ctx.globalAlpha = 1;
                }
            }
        });
    }

    drawTrackSections() {
        // Draw section indicators
        this.ctx.font = 'bold 12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        // Mark key track sections with labels
        const sectionMarkers = {
            30: 'Sainte Devote',
            96: 'Casino Square', 
            132: 'Hairpin',
            207: 'Tunnel Entrance',
            243: 'Swimming Pool',
            258: 'Rascasse'
        };

        Object.entries(sectionMarkers).forEach(([id, name]) => {
            const space = this.trackData.spaces.find(s => s.id === parseInt(id));
            if (space) {
                // Draw section label
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                this.ctx.fillText(name, space.x, space.y - 25);
                
                // Draw section marker
                this.ctx.fillStyle = 'rgba(255, 0, 0, 0.8)';
                this.ctx.beginPath();
                this.ctx.arc(space.x, space.y, 8, 0, Math.PI * 2);
                this.ctx.fill();
            }
        });
    }

    drawValidMoves(player, gear, movement) {
        // Highlight valid moves for current player
        const currentSpace = this.trackData.spaces.find(s => s.id === player.current_space);
        if (!currentSpace) return;

        // Calculate valid movement range based on gear
        const maxMove = this.getMaxMoveForGear(gear);
        const validLanes = this.getValidLanes(currentSpace, movement);

        // Highlight reachable spaces
        this.trackData.spaces.forEach(space => {
            const distance = Math.abs(space.id - currentSpace.id);
            if (distance <= maxMove && validLanes.includes(space.lane)) {
                this.ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
                this.ctx.beginPath();
                this.ctx.arc(space.x, space.y, 6, 0, Math.PI * 2);
                this.ctx.fill();
            }
        });
    }

    getMaxMoveForGear(gear) {
        // Simplified gear-to-movement mapping
        const gearMoves = {
            1: 4,   // d4
            2: 6,   // d6
            3: 8,   // d8
            4: 12,  // d12
            5: 20,  // d20
            6: 25   // d30
        };
        return gearMoves[gear] || 0;
    }

    getValidLanes(currentSpace, movement) {
        const laneCount = currentSpace.total_lanes || 3;
        const currentLane = currentSpace.lane;
        const validLanes = new Set([currentLane]);

        // Can change 1 lane per 2 spaces moved
        if (movement >= 3) {
            for (let i = 0; i < laneCount; i++) {
                validLanes.add(i);
            }
        } else if (movement >= 1) {
            // Can change 1 lane per space moved
            if (currentLane > 0) validLanes.add(currentLane - 1);
            if (currentLane < laneCount - 1) validLanes.add(currentLane + 1);
        }

        return Array.from(validLanes);
    }

    animateCarMovement(fromSpace, toSpace, duration = 500) {
        // Smooth car movement animation
        return new Promise(resolve => {
            const steps = 10;
            let currentStep = 0;

            const animate = () => {
                currentStep++;
                
                const progress = currentStep / steps;
                const currentX = fromSpace.x + (toSpace.x - fromSpace.x) * progress;
                const currentY = fromSpace.y + (toSpace.y - fromSpace.y) * progress;

                // Draw car at current position
                this.drawCarAt(currentX, currentY, progress);

                if (currentStep < steps) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };

            requestAnimationFrame(animate);
        });
    }

    drawCarAt(x, y, progress) {
        // Enhanced car rendering with rotation
        this.ctx.save();
        this.ctx.translate(x * this.scale + this.offsetX, y * this.scale + this.offsetY);
        
        // Fade effect based on progress
        this.ctx.globalAlpha = 0.5 + 0.5 * progress;
        
        // Draw car shadow
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        this.ctx.beginPath();
        this.ctx.arc(3, 3, 10, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Draw car body
        this.ctx.fillStyle = '#ff0';
        this.ctx.beginPath();
        this.ctx.arc(0, 0, 8, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.restore();
    }

    update(newTrackData) {
        this.trackData = newTrackData;
    }

    render(gameState) {
        console.log('Rendering game state:', gameState);
        console.log('Track data spaces:', this.trackData.spaces.length);
        
        this.clear();
        this.drawLaneBoundaries();
        this.drawCornerZones();
        this.drawTrackSections();
        
        // Draw cars
        gameState.players.forEach((player, idx) => {
            console.log(`Drawing player ${idx}: ${player.name} at space ${player.current_space}`);
            this.drawPlayerCar(player, idx, gameState);
        });
    }

drawPlayerCar(player, playerIndex, gameState) {
        const space = this.trackData.spaces.find(s => s.id === player.current_space);
        console.log(`Finding space for ${player.name}: looking for id ${player.current_space}, found:`, space);
        if (!space) {
            console.error(`No space found for player ${player.name} at position ${player.current_space}`);
            return;
        }

        const x = space.x * this.scale + this.offsetX;
        const y = space.y * this.scale + this.offsetY;

        console.log(`Drawing ${player.name} at (${x}, ${y}) from space (${space.x}, ${space.y})`);

        // Enhanced car rendering
        this.ctx.save();
        this.ctx.translate(x, y);

        // Remove test circle - just draw car

        // Car shadow
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        this.ctx.beginPath();
        this.ctx.arc(0, 0, 8, 0, Math.PI * 2);
        this.ctx.fill();

        // Car body
        const carColors = ['#ff0', '#0ff', '#f0f', '#0f0', '#f80', '#08f', '#f08', '#8f0'];
        this.ctx.fillStyle = carColors[playerIndex % carColors.length];
        this.ctx.beginPath();
        this.ctx.arc(0, 0, 7, 0, Math.PI * 2);
        this.ctx.fill();

        // Car outline
        this.ctx.strokeStyle = '#000';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Gear number
        this.ctx.fillStyle = '#000';
        this.ctx.font = 'bold 10px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(player.current_gear.toString(), 0, 0);

        // Player name
        this.ctx.fillStyle = carColors[playerIndex % carColors.length];
        this.ctx.font = 'bold 9px Arial';
        this.ctx.fillText(player.name, 0, -12);
        
        // Add player status indicator
        if (player.is_eliminated) {
            this.ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
            this.ctx.beginPath();
            this.ctx.arc(0, 0, 12, 0, Math.PI * 2);
            this.ctx.fill();
        }
        
        // Damage indicators
        if (player.damage) {
            let damageCount = 0;
            for (const [type, value] of Object.entries(player.damage)) {
                if (value < 18) damageCount += (18 - value);
            }
            if (damageCount > 0) {
                this.ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
                this.ctx.beginPath();
                this.ctx.arc(15, -15, 3, 0, Math.PI * 2);
                this.ctx.fill();
                this.ctx.fillStyle = '#fff';
                this.ctx.font = 'bold 8px Arial';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(damageCount.toString(), 15, -15);
            }
        }

        this.ctx.restore();
    }
}

// Export for use in main game
window.TrackVisualizer = TrackVisualizer;