# cs221-project
Scoring mine sweeper ML project

Actions: click, flag, hint, quit
<p>To calculate score:</p>
<ul>
<li>click x,y: -20 if mine, +1 if not mine.</li>
<li>flag x,y: +(30 + Remaining cells) if mine, -5 if not mine</li>
<li>hint: -3, gives a location of a mine.</li>
<li>if (x,y) is already explored: -50 (so that we won't stuck in loop)</li>
</ul>
End: quit, or all the positions have been explored.

## UI-version (for human interaction):

python simulator.py human LENGTH WIDTH MINES

where LENGTH, WIDTH, MINES define the random board you want to create.

## commandline-version (for running various models and compare):

python game.py AGENT LENGTH WIDTH MINES NUM_TIMES=1

where AGENT is {baseline, qlearning}, and NUM_TIMES is default to 1 if not specified.

python game.py compare

This will run a thorough analysis on qlearning score v.s. baseline score (average score of 1000 games). It will be run on board size [3, 6, 9, 12, 16] * [3, 6, 9, 12, 16] with mine density [0.1, 0.25, 0.5, 0.7]. Since it runs 1000 games for 100 times, expect this to finish in ~1-2hrs. We use 10000 episodes to train each qlearning.

This functionality will be useful when we generate the data for the report.

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
