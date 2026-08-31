import os
import random
import json
import requests
from uci import Uci

API_TOKEN = os.getenv("API_TOKEN")

class lichessBot:
    def __init__(self, base_time: int, increment: int, cur_rating: int, rating_range: int = 100, batch_size: int = 3, is_rated: bool = True):
        """base_time and increment are counted by seconds"""

        self.headers = {'Authorization': f'Bearer {API_TOKEN}'}

        self.base_time = base_time
        self.increment = increment
        if self.base_time <= 0 or self.increment < 0:
            raise KeyError('Base_time cannot be less than or equal to zero, increment cannot be less than zero')

        # calculate time control
        estimated_seconds = self.base_time + self.increment * 40
        if 0 < estimated_seconds <= 30:
            self.time_control = 'ultraBullet'
        elif estimated_seconds <= 180:
            self.time_control = 'bullet'
        elif estimated_seconds <= 480:
            self.time_control = 'blitz'
        elif estimated_seconds <= 1499:
            self.time_control = 'rapid'
        elif estimated_seconds >= 1500:
            self.time_control = 'classical'

        self.cur_rating = cur_rating
        self.rating_range = rating_range

        self.batch_size = batch_size
        self.is_rated = is_rated

    def choose_in_challenges(self, challenge_list_resp) -> str:
        challenge_list = challenge_list_resp.json()
        for challenge in challenge_list['in']:

            if challenge['speed'] == self.time_control and challenge['variant']['key'] == 'standard' and challenge['rated'] == self.is_rated:
                rating = challenge['challenger']['rating']

                if self.cur_rating - self.rating_range <= rating <= self.cur_rating + self.rating_range:
                    return challenge['id']

        return ''

    def get_opponents(self, online_bots_resp) -> list[str]:
        """returns id of possible opponents"""
        
        online_bots = online_bots_resp.text.split('\n')
        opponents = []

        for line in online_bots:
            bot = json.loads(line)
            rating = bot['perfs'][self.time_control]['rating']

            if self.cur_rating - self.rating_range <= rating <= self.cur_rating + self.rating_range:
                opponents.append(bot['id'])

        return opponents

    def challenge_opponent(self, opponent_id: str) -> str:
        """
        base_time and increment are time control elements:
        Bullet: 1+0, 2+1
        Blitz: 3+0, 3+2, 5+0, 5+3
        Rapid: 8+0, 10+0, 15+10, 20+5,
        Classical: 25+0, 15+15, 30+20, 60+0
        """

        challenge_resp = requests.post(
                f"https://lichess.org/api/challenge/{opponent_id}",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Bearer {API_TOKEN}"
                },
                data={
                    "clock.limit": str(self.base_time),
                    "clock.increment": str(self.increment),
                    "rated": "false" if not self.is_rated else "true",
                    "color": "random",
                    "variant": "standard",
                    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                    "keepAliveStream": "true",
                }
            )

        challenge_resp = json.loads(challenge_resp.text.splitlines()[0])

        try:
            challenge_id = challenge_resp['id']
            print('challenge sent')
            return challenge_id
        except Exception:
            print(challenge_resp['error'])
            print('continuing to next opponent...')
            return ''

    def opponent_batches(self, opponent_ids: list[str]):
        random.shuffle(opponent_ids)    
        batch = []
        for opponent_id in opponent_ids:
            if len(batch) == self.batch_size - 1:
                batch.append(opponent_id)
                yield batch
                batch = []
            else:
                batch.append(opponent_id)
        if batch:
            yield batch

    def cancel_challenges(self, challenge_ids, game_id=''):
        for challenge_id in challenge_ids:
            if challenge_id and challenge_id != game_id:
                cancel_resp = requests.post(
                    f"https://lichess.org/api/challenge/{challenge_id}/cancel",
                    headers=self.headers,
                ).json()
                try:
                    cancel_successful = cancel_resp['ok']
                    print('Challenge cancelled successfully')
                except Exception:
                    print('Cancel challenge failed')

    def get_game(self):
        challenge_list_resp = requests.get("https://lichess.org/api/challenge",
            headers=self.headers
        )
        print('challenge_list request successful')

        game_id = self.choose_in_challenges(challenge_list_resp, self.time_control, self.cur_rating, self.rating_range)
        in_challenge_successfull = False

        if game_id:
            in_challenge_successfull = requests.post(
                f"https://lichess.org/api/challenge/{game_id}/accept",
                headers=self.headers
            )

            try:
                in_challenge_successfull = in_challenge_successfull['ok']
                print('successfully taken in challenge')
            except Exception:
                print('in challenge cancelled')

        if not game_id or not in_challenge_successfull:
            num_bot_resp = requests.get("https://lichess.org/api/bot/online?nb=512")
            print('online bots request successful')
            opponent_ids = self.get_opponents(num_bot_resp, self.time_control, self.cur_rating, self.rating_range)
            game_found = False

            for opponent_batch in self.opponent_batches(opponent_ids, batch_size=self.batch_size):
                challenge_ids = []

                for opponent_id in opponent_batch:
                    challenge_id = self.challenge_opponent(opponent_id, is_rated=self.is_rated, base_time=self.base_time, increment=self.increment)
                    challenge_ids.append(challenge_id)

                with requests.get("https://lichess.org/api/stream/event", headers=self.headers, stream=True) as resp:
                    keep_alive_count = 0

                    for event in resp.iter_lines():
                        if event:
                            game = json.loads(event)

                            if game['type'] == 'gameStart':
                                game_id, color = game['game']['gameId'], game['game']['color']
                                game_found = True
                                print(game_id)

                                self.cancel_challenges(challenge_ids, game_id)
                                break
                            
                        else:
                            print('waiting for response...')
                            keep_alive_count += 1
                            print('current count till next round: ' + str(5 - keep_alive_count))
                            if keep_alive_count >= 5:
                                
                                self.cancel_challenges(challenge_ids)
                                print('---Starting next round---')
                                break
            
                if game_found:
                    break
        if game_found:
            return game_id, color
        else:
            self.get_game()

    def get_move(self):
        pass

    def make_move(self):
        pass
