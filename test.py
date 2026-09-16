import requests
import json
from environment.move import Move
from environment.board import Board
from lichessBot.bot import END_STATUS, API_TOKEN
from lichessBot.bot import Uci
from agent.testAgent import TestAgent

agent = TestAgent()
board = Board()
uci_interpreter = Uci(board)
header = {'Authorization': f'Bearer {API_TOKEN}'}
game_present = True
game_id = 'PFBraqbQS718'
color = 'w'

def pending_move() -> Move | None:
    global game_present, game_id
    with requests.get(f"https://lichess.org/api/bot/game/stream/{game_id}",headers=header, stream=True) as resp:

        for event in resp.iter_lines():
            if event:
                event = json.loads(event)

                try:
                    event_type = event['type']
                except KeyError:
                    raise RuntimeError("Wrong game ID or internet connection issues")

                if event_type == 'gameFull':
                    event = event['state']
                    event_type = 'gameState'

                if event_type == "gameState":
                    move_sequence: str = event['moves']
                    move = uci_interpreter.get_move_from_uci(move_sequence)
                    if event['status'] in END_STATUS:
                        game_present = False
                    if isinstance(move, Move):
                        return move
                    else:
                        continue
                        
                if event_type == "opponentGone":
                    if event['claimWinInSeconds'] <= 0:
                        game_present = False
                        requests.post(
                            f"https://lichess.org/api/bot/game/{game_id}/claim-draw",
                            headers=header
                        )
                        return 
                    
def make_move(move: Move):
    global game_id
    if game_present:
        move_uci = uci_interpreter.add_move_uci(move)
        move_resp = requests.post(
            f"https://lichess.org/api/bot/game/{game_id}/move/{move_uci}",
            headers=header
        )
        try:
            move_made_successful = move_resp.json()['ok']
        except KeyError:
            raise RuntimeError(f"Problem with request code or problem with enviroment logic. Move uci: {move_uci}")

if __name__ == "__main__":
    if color == 'w':
        moves = board.all_moves()
        agent_move = agent.choose_action(moves)
        make_move(agent_move)
        board.move(agent_move)
        print("agent move made")
    while game_present:
        opponent_move = pending_move()
        print("opponent move made")
        if not game_present:
            break
        board.move(opponent_move)
        moves = board.all_moves()
        agent_move = agent.choose_action(moves)
        make_move(agent_move)
        print("agent move made")
        board.move(agent_move)
