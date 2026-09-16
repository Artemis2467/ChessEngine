import requests
from time import sleep
from lichessBot.bot import LichessBot
from agent.testAgent import TestAgent

RETRY_MAX = 10

if __name__ == "__main__":
    agent = TestAgent()
    bot = LichessBot(base_time=900, increment=10, cur_rating=1500, is_rated=False)

    while True:

        try:
            retry_count = RETRY_MAX
            bot.get_game()
            print(bot.color)
            if bot.color == 'w':
                moves = bot.board.all_moves()
                agent_move = agent.choose_action(moves)
                bot.make_move(agent_move)
                bot.board.move(agent_move)
                print("agent move made")
            while bot.game_present:
                opponent_move = bot.pending_move()
                print("opponent move made")
                if not bot.game_present:
                    break
                bot.board.move(opponent_move)
                moves = bot.board.all_moves()
                agent_move = agent.choose_action(moves)
                bot.make_move(agent_move)
                print("agent move made")
                bot.board.move(agent_move)

        except requests.ConnectionError:
            if retry_count == RETRY_MAX:
                print("A connection error has occured")
            if retry_count > 0:
                print(f"retry left: {retry_count}")
                print("retry in ...")
                for i in range(10, 0, -1):
                    print(i)
                    sleep(1)
                continue
            else:
                print("Stopped due to connection issues")
                break
