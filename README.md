# networkPythonProject
The repository for the 2nd Semester Python Project

# Installation guide

**Step 1: Clone the project**
```
git clone https://github.com/tkdev1755/networkPythonProject.git
```
**Step 2: Go to project directory**
```
cd networkPythonProject
```

We have two versions of the project:
    - A stable and inconsistent version in the V3.5 branch
    - A consistent version with some bug sometimes in the NetworkPropertyVersion branch

# Run the game

You can start the game by running the ```main.py``` file:
```
python3 backend/main.py
```

After that, you can compile and execute le networkEngine.c file with this command :
In a Windows OS
```
gcc network/networkEngine.c network/includes/network.c -o networkEngine -lws2_32 -liphlpapi
```
In Linux OS
```
gcc network/networkEngine.c network/includes/network.c -o networkEngine
```
Then run it 
```
./networkEngine
```

For Windows, you have to start the python file first before the C program if you are joinning the game.

Once the python file lunched, press F9 to run the GUI mode and back to the terminal and press n to start AI actions.

And enjoy the simulation.

Python based code borrowed from Nathan & Friends 
THANK YOU VERY MUCH !

