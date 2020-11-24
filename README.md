# Wumpus World Simulations using Python and Pomegranate

This version of the Wumpus World game uses Probablistic Agent to navigate the world and avoids Wumpus and Pits based on probability of there being a risk of of either.

- Use __Jupyter Notebook (Assignment 3 - SCS_3547_008-simulator.ipynb)__ file for better display of output
- Use __Python Script (simulator.py)__ for faster runtime and quicker output for 1000 simulations. It will log output in __simulator_output.log__
- __ipynb__ also has sample runs which can be used to debug any simulation.
- For debugging purposes, every simulation outputs an override command at the very end, which can be used to fix wumpus, gold and pits locations on the layout for that specific random configuration. Example:
```python
env.override( wumpus_loc=P(1,2), pits_loc=[P(0,1), P(0,3), P(1,2), P(2,2), P(2,3)], gold_loc=P(3,3) )
```

- Results for 1000 run simulation in python script:

<pre>
======================================= AGGREGATE STATISTICS FOR 1000 RUNS ========================================
+-----------------+--------------+----------------+-------------------+----------------------+--------------------+
|   Total Rewards |   Total Wins |   Total Losses |   Total Abondoned |   Total Wumpus Kills |   Total Pits Faced |
+=================+==============+================+===================+======================+====================+
|           82678 |          359 |            262 |               379 |                  123 |               2997 |
+-----------------+--------------+----------------+-------------------+----------------------+--------------------+
</pre>

- Results for 100 run simulation in __ipynb__:

<pre>
======================================== AGGREGATE STATISTICS FOR 100 RUNS ========================================
+-----------------+--------------+----------------+-------------------+----------------------+--------------------+
|   Total Rewards |   Total Wins |   Total Losses |   Total Abondoned |   Total Wumpus Kills |   Total Pits Faced |
+=================+==============+================+===================+======================+====================+
|           13516 |           39 |             24 |                37 |                   10 |                271 |
+-----------------+--------------+----------------+-------------------+----------------------+--------------------+
</pre>
