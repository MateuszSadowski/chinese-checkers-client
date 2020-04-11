import asyncio
import datetime
import time

import helper

reference = {
    'depth': 1,
    'weight': 0.5,
    'algorithm': 'Minmax'
}
games = [
    {
        'gameId': 42,
        'testPlayer': {
            'depth': 2,
            'weight': 0.5,
            'algorithm': 'MinmaxNoprun'
        },
        'refPlayer': reference
    }
    # ,
    #     {
    #     'gameId': 41,
    #     'testPlayer': {
    #         'depth': 1,
    #         'weight': 0.7,
    #         'algorithm': 'Minmax'
    #     },
    #     'refPlayer': reference
    # },
]

async def run(cmd, stdout, stderr):
    proc = await asyncio.create_subprocess_exec(
        cmd[0],
        *cmd[1:],
        stdout=stdout,
        stderr=stderr)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd[0]!r} exited with {proc.returncode}]')
    # if stdout:
    #     print(f'[stdout]\n{stdout.decode()}')
    # if stderr:
    #     print(f'[stderr]\n{stderr.decode()}')

for game in games:
    gameId = game['gameId']

    testMaxDepth = game['testPlayer']['depth']
    testEvalWeight = game['testPlayer']['weight']
    testAlgorithm = game['testPlayer']['algorithm']

    refMaxDepth = game['refPlayer']['depth']
    refEvalWeight = game['refPlayer']['weight']
    refAlgorithm = game['refPlayer']['algorithm']

    gameFolder = 'stats/{0}-game-{1}-{2}-depth{3}-weight{4}-vs-{5}-depth{6}-weight{7}'.format(gameId, datetime.datetime.now().isoformat(), testAlgorithm, testMaxDepth, testEvalWeight, refAlgorithm, refMaxDepth, refEvalWeight)

    testStdoutFileName = gameFolder + '/test_stdout.txt'
    helper.createDirs(testStdoutFileName)
    testStdoutFile = open(testStdoutFileName, 'w+', newline='')

    refStdoutFileName = gameFolder + '/ref_stdout.txt'
    helper.createDirs(refStdoutFileName)
    refStdoutFile = open(refStdoutFileName, 'w+', newline='')

    async def runGames():
        print('Running {0} depth {1} weight {2} on gameId {3}...'.format(testAlgorithm, testMaxDepth, testEvalWeight, gameId))
        print('Running {0} depth {1} weight {2} on gameId {3}...\n'.format(refAlgorithm, refMaxDepth, refEvalWeight, gameId))
        testCmd = ["python3", "client" + testAlgorithm + ".py", "-d " + str(testMaxDepth), "-w " + str(testEvalWeight), "-g " + str(gameId)]
        refCmd = ["python3", "client" + refAlgorithm + ".py", "-d " + str(refMaxDepth), "-w " + str(refEvalWeight), "-g " + str(gameId)]
        await asyncio.gather(
            run(testCmd, testStdoutFile, asyncio.subprocess.STDOUT),
            run(refCmd, refStdoutFile, asyncio.subprocess.STDOUT) 
        )
    asyncio.run(runGames())

    print('Game finished.\n')
    print('Output logged to folder:')
    print(gameFolder)
    print('')

print('All games finished.\n')