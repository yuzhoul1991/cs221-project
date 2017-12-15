# cs221-project
Scoring mine sweeper ML project

Actions: click, flag, hint, quit
<p>To calculate score:</p>
<ul>
<li>click x,y: -10 if mine, +2 if not mine.</li>
<li>flag x,y: +15 if mine, -10 if not mine</li>
<li>hint: -3, gives a location of a mine.</li>
<li>if (x,y) is already explored: -50 (so that we won't stuck in loop)</li>
</ul>
End: quit, or all the positions have been explored.

## UI-version (for human interaction):

python simulator.py human LENGTH WIDTH MINES

where LENGTH, WIDTH, MINES define the random board you want to create.

## commandline-version (for running various models and compare):

python game.py AGENT LENGTH WIDTH MINES NUM_TIMES=1 NUM_EPISODES=10000 {"with_baseline"}

where AGENT is {baseline, qlearning, csp}, and NUM_TIMES is default to 1 if not specified. NUM_EPISODES is only valid when AGENT is qlearning, and it represents how much episodes it trains from (default 10000). If "with_baseline" is added as the 7th argument, then the model will run with basic baseline logic.

python nn_qlearning.py LENGTH WIDTH MINES

This will invoke the qlearning with heuristics trained from NN (instead of our own features).


## commandline-version (for human interaction, not recommended):

python game.py human

<p>Available commands:</p>
<ul>
<li>start x y z: start a game with x*y and z mine.</li>
<li>click x y: click on x, y</li>
<li>hint: gives the location of a random mine.</li>
<li>flag x y: flag on x, y</li>
<li>score: current score</li>
<li>print: print current player board</li>
<li>print x: print the correct board (cheating :))</li>
<li>quit: quit the current game</li>
</ul>
