# cs221-project
Scoring mine sweeper ML project

For human:

python game.py human
Actions: click, flag, hint, quit
<p>To calculate score:</p>
<ul>
<li>click x,y: -20 if mine, +1 if not mine.</li>
<li>flag x,y: +(30 + Remaining cells) if mine, -5 if not mine</li>
<li>hint: -3, gives a location of a mine.</li>
<li>if (x,y) is already explored: -50 (so that we won't stuck in loop)</li>
</ul>
End: quit, or all the positions have been explored.

To interact with the file:
python game.py
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
