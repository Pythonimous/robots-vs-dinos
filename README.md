# Coding Challenge - Robots vs Dinosaurs

My take on the [Grover coding assignment][1].

The solution is based on Flask and flask-restx.

## Features:
- Create an empty simulation space - an empty custom-size grid;
- Create a robot in a certain position and facing direction;
- Create a dinosaur in a certain position;
- Issue instructions to a robot:
  - Turn left, turn right, move forward, move backward, and attack;
- A robot's attack DAMAGES dinosaurs around it (in front, to the left, to the right or behind). If the dino's health is 0, it is destroyed;
- Display healthbars;
- Display the simulation's current state;
- Two or more entities (robots or dinosaurs) cannot occupy the same position;
- Attempting to move a robot outside the simulation space is an invalid operation.


## Installation

Install project requirements from [requirements.txt][2]:

```bash
pip3 install -r requirements.txt
```

## Testing
In order to confirm that the scripts are functional after the installation, use:
```bash
python3 -m unittest
```
You can additionally check detailed test coverage using the [**coverage**](https://coverage.readthedocs.io/en/6.3.2/) library for Python. You can install it via:
```bash
pip3 install coverage
```
Before generating the report, you need to run the tests with **coverage**. Current test coverage is **100%**:
```bash
coverage run -m unittest
```
A simple report can then be generated using:
```bash
coverage report
```

[1]: https://github.com/devsbb/grover-engineering-recruitment/blob/master/challenges/robots-vs-dinos/ASSIGNMENT.md
[2]: https://github.com/Pythonimous/robots-vs-dinos/blob/main/requirements.txt
