# Wumpus World Simulations using Python

This version of the Wumpus World game uses Probablistic Agent to navigate the world and avoids Wumpus and Pits based on probability of there being a risk of of either.

- Use __ipynb__ file for better display of output
- Use __simulator.py__ for faster runtime and quicker output for 1000 simulations. It will log output in __simulator_output.log__
- __ipynb__ also has sample runs which can be used to debug any simulation.
- For debugging purposes, every simulation outputs an override command at the very end, which can be used to fix wumpus, gold and pits locations on the layout for that specific random configuration. Example:
```python
env.override( wumpus_loc=P(1,2), pits_loc=[P(0,1), P(0,3), P(1,2), P(2,2), P(2,3)], gold_loc=P(3,3) )
```
