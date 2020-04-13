import asyncio
import datetime
import time

import helper

reference = {
    'depth': 1,
    'weight': 0.5,
    'pruning': True,
    'algorithm': 'Minmax'
}
games = [
    {
        'gameId': 8,
        'testPlayer': {
            'depth': 3,
            'weight': 0.6,
            'pruning': False,
            'algorithm': 'Minmax'
        },
        'refPlayer': reference
    },
    {
        'gameId': 9,
        'testPlayer': {
            'depth': 3,
            'weight': 0.6,
            'pruning': True,
            'algorithm': 'Minmax'
        },
        'refPlayer': reference
    },
    {
        'gameId': 10,
        'testPlayer': {
            'depth': 3,
            'weight': 0.6,
            'pruning': True,
            'algorithm': 'Minmax'
        },
        'refPlayer': reference
    }
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
    testPruning = game['testPlayer']['pruning']

    refMaxDepth = game['refPlayer']['depth']
    refEvalWeight = game['refPlayer']['weight']
    refAlgorithm = game['refPlayer']['algorithm']
    refPruning = game['refPlayer']['pruning']

    gameFolder = 'stats/{0}-game-{1}-{2}-depth{3}-weight{4}-vs-{5}-depth{6}-weight{7}'.format(gameId, datetime.datetime.now().isoformat(), testAlgorithm, testMaxDepth, testEvalWeight, refAlgorithm, refMaxDepth, refEvalWeight)

    testStdoutFileName = gameFolder + '/test_stdout.txt'
    helper.createDirs(testStdoutFileName)
    testStdoutFile = open(testStdoutFileName, 'w+', newline='')

    refStdoutFileName = gameFolder + '/ref_stdout.txt'
    helper.createDirs(refStdoutFileName)
    refStdoutFile = open(refStdoutFileName, 'w+', newline='')

    async def runGames():
        print('Running {0} depth: {1}, weight: {2}, alpha-beta: {4} on gameId {3}...'.format(testAlgorithm, testMaxDepth, testEvalWeight, gameId, testPruning))
        print('Running {0} depth: {1}, weight: {2}, alpha-beta: {4} on gameId {3}...\n'.format(refAlgorithm, refMaxDepth, refEvalWeight, gameId, refPruning))
        testCmd = ["python3", "client" + testAlgorithm + ".py", "-d " + str(testMaxDepth), "-w " + str(testEvalWeight), "-g " + str(gameId)]
        refCmd = ["python3", "client" + refAlgorithm + ".py", "-d " + str(refMaxDepth), "-w " + str(refEvalWeight), "-g " + str(gameId)]
        if not testPruning:
            testCmd.append("--no-pruning")
        if not refPruning:
            refCmd.append("--no-pruning")

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