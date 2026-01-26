#!/usr/bin/env python3
"""
Test start race functionality using WebSocket
"""

import asyncio
import websockets
import json

async def test_start_race():
    """Test starting race as host"""
    # Create game first
    import requests
    res = requests.post('http://localhost:8000/create-game', 
                      json={"player_names": ["HostTest"], "dice_mode": "simple", "is_private": False})
    game_data = res.json()
    game_id = game_data['game_id']
    player_id = game_data['player_id']
    
    print(f"✅ Created game {game_id}, player_id: {player_id}")
    
    # Connect as host via WebSocket
    uri = f"ws://localhost:8000/ws/{game_id}"
    async with websockets.connect(uri) as websocket:
        print(f"🔗 Connected to {uri}")
        
        # Register as host
        register_msg = {"type": "register", "player_id": player_id}
        await websocket.send(json.dumps(register_msg))
        print(f"📝 Sent register: {register_msg}")
        
        # Wait for state
        response = await websocket.recv()
        state_data = json.loads(response)
        print(f"📊 Received state: {state_data.get('type', 'unknown')}")
        
        # Try to start race
        start_msg = {"type": "start_race"}
        await websocket.send(json.dumps(start_msg))
        print(f"🏁 Sent start race: {start_msg}")
        
        # Wait for updated state
        response = await websocket.recv()
        updated_state = json.loads(response)
        print(f"🏁 Updated state - race started: {updated_state.get('state', {}).get('race_started', False)}")

if __name__ == "__main__":
    try:
        asyncio.run(test_start_race())
    except Exception as e:
        print(f"❌ Error: {e}")