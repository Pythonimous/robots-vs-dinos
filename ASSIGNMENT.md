# Coding Challenge - Robots vs Dinosaurs

Grover is assembling an army of remote-controlled robots to fight the dinosaurs and the first step towards that is to run simulations on how they will perform. You are tasked with implementing a service that provides a REST API to support those simulations.

## These are the features required:

- Be able to create an empty simulation space - an empty 50 x 50 grid - DONE (custom size);
- Be able to create a robot in a certain position and facing direction - DONE;
- Be able to create a dinosaur in a certain position - DONE;
- Issue instructions to a robot - a robot can turn left, turn right, move forward, move backward, and attack - DONE;
- A robot attack destroys dinosaurs around it (in front, to the left, to the right or behind)  - DONE;
- No need to worry about the dinosaurs - dinosaurs don't move - DONE;
- Display the simulation's current state - DONE;
- Two or more entities (robots or dinosaurs) cannot occupy the same position - DONE;
- Attempting to move a robot outside the simulation space is an invalid operation - DONE.

## Things we are looking for

- Immutability/Referential transparency;
- Idiomatic code;
- Adherence to community/standard library style guides;
- Separation of concerns;
- Unit and integration tests;
- API design;
- Domain modeling;
- Attention to possible concurrency issues;
- Error handling.
