import asyncio
from collections import namedtuple
from enum import Enum
import logging
import sys
import random

"""
Namedtuples work like classes, but are much more lightweight so they end
up being faster. It would be a good idea to keep objects in each of these
for each game which contain the game's state, for instance things like the
socket, the cards given, the cards still available, etc.
"""
Game = namedtuple("Game", ["p1", "p2"])

SUCCESS = 'Test should trigger an error.'

class Command(Enum):
    """
    The byte values sent as the first byte of any message in the war protocol.
    """
    WANTGAME = 0
    GAMESTART = 1
    PLAYCARD = 2
    PLAYRESULT = 3


class Result(Enum):
    """
    The byte values sent as the payload byte of a PLAYRESULT message.
    """
    WIN = 0
    DRAW = 1
    LOSE = 2


async def limit_client(host, port, loop, sem, tc):
    """
    Limit the number of clients currently executing.
    You do not need to change this function.
    """

    async with sem:
        return await client(host, port, loop, tc)


async def client(host, port, loop, testcase):
    """
    Run an individual client on a given event loop.
    You do not need to change this function.
    """

    global SUCCESS
    try:

        reader, writer = await asyncio.open_connection(host, port, loop=loop)
        # send want game
        myscore = 0

        writer.write(b"\0\0")
        card_msg = await reader.readexactly(27)



        if testcase == 'tc1':
            SUCCESS = "Test should NOT trigger an error"
            # print('TESTING: Randomizing client cards then sending back client')
            # print('Expected: Successful (unless Prof. Kanich says otherwise)')
            shuffle_cards = []
            all_cards = []
            for card in card_msg[1:]:
                shuffle_cards.append(card)
            random.shuffle(shuffle_cards)
            for card in shuffle_cards:
                all_cards.append(Command.PLAYCARD.value)
                all_cards.append(card)


            writer.write(bytearray(all_cards))
            i = 0;
            while i < 26:
                result = await reader.readexactly(2)
                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1
                i += 1




        if testcase == 'tc2':
            SUCCESS = "Test should NOT trigger an error"
            # print('TESTING: Send 1 card, 12 cards, then the last 13 cards')
            # print('Expected: Successful')
            all_cards = []
            for cards in card_msg[1:]:
                all_cards.append(cards)

            partial_cards = []
            partial_cards.append(Command.PLAYCARD.value)
            partial_cards.append(card_msg[1])

            await asyncio.sleep(3)
            writer.write(bytes(partial_cards))
            result = await reader.readexactly(2)
            if result[1] == Result.WIN.value:
                myscore += 1
            elif result[1] == Result.LOSE.value:
                myscore -= 1

            partial_cards = []
            i = 2
            while i < 14:
                partial_cards.append(Command.PLAYCARD.value)
                partial_cards.append(card_msg[i])
                i += 1

            await asyncio.sleep(3)
            writer.write(bytes(partial_cards))
            i = 0
            while i < 12:
                result = await reader.readexactly(2)
                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1
                i += 1

            i += 2
            partial_cards = []
            while i < 27:
                partial_cards.append(Command.PLAYCARD.value)
                partial_cards.append(card_msg[i])
                i += 1

            await asyncio.sleep(3)
            writer.write(bytes(partial_cards))

            i = 0
            while i < 12:
                result = await reader.readexactly(2)
                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1
                i += 1




        if testcase == 'tc3':
            SUCCESS = "Test should trigger an error from server."
            # print('TESTING: Send 1 card. Nothing else.')
            # print('Expected: Should get an IncompleteReadError from server terminal. It should timeout')
            partial_cards = []
            partial_cards.append(Command.PLAYCARD.value)
            partial_cards.append(card_msg[1])
            await asyncio.sleep(3)
            writer.write(bytes(partial_cards))
            result = await reader.readexactly(2)
            if result[1] == Result.WIN.value:
                myscore += 1
            elif result[1] == Result.LOSE.value:
                myscore -= 1



        if testcase == 'tc4':
            SUCCESS = "Test should NOT trigger an error"
            # print('TESTING: Sending all cards at the same time')
            # print('Expected: Successful')
            all_cards = []
            for card in card_msg[1:]:
                all_cards.append(Command.PLAYCARD.value)
                all_cards.append(card)

            writer.write(bytearray(all_cards))
            i = 0;
            while i < 26:
                result = await reader.readexactly(2)
                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1
                i += 1



        if testcase == 'tc5':
            SUCCESS = "Test should NOT trigger an error"
            # print('TESTING: Sending all cards at the same time (similar to tc4, but done a little differently)')
            # print('Expected: Successful')
            for card in card_msg[1:]:
                writer.write(bytes([Command.PLAYCARD.value, card]))
            for card in card_msg[1:]:
                result = await reader.readexactly(2)
                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1




        if testcase == 'tc6':
            SUCCESS = "Test should NOT trigger an error"
            # print('TESTING: Original Test')
            # print('Expected: Successful')
            for card in card_msg[1:]:

                writer.write(bytes([Command.PLAYCARD.value, card]))
                result = await reader.readexactly(2)

                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1



        if testcase == 'tc7':
            SUCCESS = "Test should trigger an error"
            for card in card_msg[1:]:

                writer.write(bytes([Command.WANTGAME.value, card]))
                result = await reader.readexactly(2)

                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1

        if testcase == 'tc8':
            SUCCESS = "Test should trigger an error"
            for card in card_msg[1:]:

                writer.write(bytes([Command.PLAYCARD.value, card_msg[1]]))

                result = await reader.readexactly(2)

                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1

        if testcase == 'tc9':
            SUCCESS = "Test should NOT trigger an error"
            for card in card_msg[1:]:
                writer.write(bytes([Command.PLAYCARD.value]))
                await asyncio.sleep(.25)
                writer.write(bytes([card]))
                result = await reader.readexactly(2)
                if result[1] == Result.WIN.value:
                    myscore += 1
                elif result[1] == Result.LOSE.value:
                    myscore -= 1

        if myscore > 0:
            result = "won"
        elif myscore < 0:
            result = "lost"
        else:
            result = "drew"

        print("Result: ", result)
        logging.debug("Game complete, I %s", result)
        writer.close()
        return 1
    except ConnectionResetError:
        logging.error("ConnectionResetError")
        return 0
    except asyncio.streams.IncompleteReadError:
        logging.error("asyncio.streams.IncompleteReadError")
        return 0
    except OSError:
        logging.error("OSError")
        return 0


def main(args):
    """
    launch a client/server
    """
    host = args[1]
    port = int(args[2])
    testcase = args[3]

    loop = asyncio.get_event_loop()

    if args[0] == "client":
        loop.run_until_complete(client(host, port, loop, testcase))
    elif args[0] == "clients":
        sem = asyncio.Semaphore(1000)
        num_clients = int(args[4])
        clients = [limit_client(host, port, loop, sem, testcase)
                   for x in range(num_clients)]

        async def run_all_clients():
            """
            use `as_completed` to spawn all clients simultaneously
            and collect their results in arbitrary order.
            """
            completed_clients = 0
            for client_result in asyncio.as_completed(clients):
                completed_clients += await client_result
            return completed_clients

        res = loop.run_until_complete(asyncio.Task(run_all_clients(), loop=loop))
        logging.info("STATUS: %s", SUCCESS)
        logging.info("%d completed clients", res)

    loop.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
