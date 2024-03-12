import matplotlib.pyplot as plt
import numpy as np
import time
import matplotlib.animation as animation

from utils import *
from grid import *

def gen_polygons(worldfilepath):
    polygons = []
    with open(worldfilepath, "r") as f:
        lines = f.readlines()
        lines = [line[:-1] for line in lines]
        for line in lines:
            polygon = []
            pts = line.split(';')
            for pt in pts:
                xy = pt.split(',')
                polygon.append(Point(int(xy[0]), int(xy[1])))
            polygons.append(polygon)
    return polygons


class Node:
    def __init__(self, state, parent=None, action=None, pathCost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.pathCost = pathCost

    def __lt__(self, other):
        return self.pathCost < other.pathCost

    
    def expand(self, problem):
        outList = []
        for action in problem.actions(self.state):
            newCost = self.pathCost + problem.pathCost(0, self.state, action, None)  # update path cost based on action
            outList.append(Node(action, self, action, newCost))
        return outList

    def expandWithCost(self, problem):
            outList = []
            for action in problem.actions(self.state):
                cost = 1.5 if problem.isturfs(action) else 1
                newCost = self.pathCost + cost  # update path cost for each action
                outList.append(Node(action, self, action, newCost))
            return outList
    
    
    def childNode(self, problem, action):
        nextState = problem.result(self.state, action)
        return Node(nextState, self, action, problem.pathCost(self.pathCost, self.state, action, nextState))

    


class Problem:
    def __init__(self, initial, goal, gridWidth, gridHeight, obstacles,turfs):
        self.initial = initial
        self.goal = goal
        self.gridWidth = gridWidth
        self.gridHeight = gridHeight
        self.obstacles = obstacles
        self.turfs = turfs
        
    def actions(self, state):
        # assuming a simple grid where you can move in four directions from any given point
        actions = []
        # up, right, down, left
        for dy, dx in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
            newX, newY = state[0] + dx, state[1] + dy
            # check for edges
            if (newX < 0) or (newX >= self.gridWidth) or (newY < 0) or (newY >= self.gridHeight):
                continue
            # check for obstacles
            #if 0 <= newX < self.gridWidth and 0 <= newY < self.gridHeight:
            if not self.isObstacle((newX, newY)):
                actions.append((newX, newY))            
        return actions
    def result(self, state, action):
        newState = (state[0] + action[0], state[1] + action[1])
        return newState

    def isGoal(self, state):
        return state == self.goal

    def pathCost(self, c, state1, action, state2):
        return c + 1  # Assuming uniform path cost
    
    def isObstacle(self, state):
        return state in self.obstacles
    
    def isturfs(self, state):
        return state in self.turfs
    
    def heuristic(self,state, goal):
        #Euclidean distance as heuristic
        return np.sqrt((state[0] - goal[0]) ** 2 +(state[1]-goal[1])**2)

#straight from the slide and textbook is

def bfs(problem):
    initNode = Node(problem.initial)
    #print(f"Starting BFS with initial node: {initNode.state}")
    if problem.isGoal(initNode.state):
        #print("Initial node is the goal.")
        return initNode
    frontier = Queue()
    frontier.push(initNode)
    reached = set()
    reached.add(problem.initial)
    while not frontier.isEmpty():
        currentNode = frontier.pop()
        #print(currentNode.expand(problem))
        #print(f"Exploring node: {currentNode.state}")
        for childNode in currentNode.expand(problem):
            #print(f"Child node: {childNode.state == problem.goal}")
            if problem.isGoal(childNode.state):
                print(f"Goal found: {childNode.state}")
                return childNode
            #print("current node",currentNode.state)
            #print("child node", childNode.state)
            if childNode.state not in reached:
                #print(f"Child node: {childNode.state}")
                reached.add(childNode.state)
                frontier.push(childNode)
    print("No path found after BFS.")
    return None


#straight from the slides is-cycle is replaced with the idea of visited

def dfs(problem):
    result = None
    vistied = set()
    frontier = Stack()
    initNode = Node(problem.initial)
    #if problem.isGoal(initNode.state):
    #    return initNode
    frontier.push(initNode)
    #vistied.add(initNode.state)
    while not frontier.isEmpty():        
         node = frontier.pop()
         vistied.add(node.state)
         if problem.isGoal(node.state):
             result = node
             return result
         for child in node.expand(problem):
             #print(child.state)
             if not child.state in vistied:
                #vistied.add(child.state)
                frontier.push(child)
             #else:
                #break

    return result

#GBFS based off of BFS but also no found exact code reference to this in slides or textbook citation below


def greedyBestFirstSearch(problem):
    node = Node(problem.initial,pathCost=0)
    frontier = PriorityQueue()
    frontier.push(node, problem.heuristic(node.state,problem.goal))
    reached = {node.state: node}
    nextChild = None
    while not frontier.isEmpty():
        node = frontier.pop()
        if problem.isGoal(node.state):
            return node
        for child in node.expandWithCost(problem):
            s = child.state
            #print(child.state)
            #print(problem.heuristic(s,problem.goal))
            minCost = 8000
            nextChild = s
            if problem.heuristic(s,problem.goal) <= minCost:
                minCost = problem.heuristic(child.state,problem.goal)
                nextChild = child
                
            if nextChild.state not in reached:
                reached[s] = nextChild
                frontier.push(nextChild, problem.heuristic(nextChild.state,problem.goal))


# this a* algo is based off a medium article on a* written in python as i could not find the algo in the slides or textbook
#https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2

def aStar(problem):
    open = PriorityQueue()
    open.push(Node(problem.initial), 0)
    visited = {}
    g = {problem.initial: 0}  #  dict to keep track of the cost from the start node to each node starting with the initial node at cost 0
    f = {problem.initial: problem.heuristic(problem.initial, problem.goal)}  # dict for the estimated total cost

    while not open.isEmpty():
        #continues until there are no more nodes to visit
        current = open.pop() #removes and returns the node with the lowest f from the open set

        if problem.isGoal(current.state): # checks to see goal
            return current

        for action in problem.actions(current.state): #possible actions from the current state

            if action in visited:
                continue
            
            tempG = g[current.state] + problem.pathCost(current.pathCost, current.state, action, action) #the tentative cost from the start node to the resulting state from the current action
            newCost = tempG + problem.heuristic(action, problem.goal)  #adds the heuristic estimate to the goal from the action state
            if action not in g or tempG < g[action]:
                visited[action] = current
                g[action] = tempG # updates g
                f[action] = newCost # updates g
                if not any(node.state == action for _, _, node in open.heap): #checks if the action state is already in the open set
                    newNode = Node(action, parent=current, pathCost=tempG) #if the action state is not in the open set then new node
                    open.push(newNode, f[action]) # adds new node with f as the prio

    return None

    
def backtrackPath(node):
    path = []
    while node.parent is not None:
        path.append(node.state)
        node = node.parent
    path.reverse()
    return path


def totalPathCost(node):
    totalCost = 0
    while node.parent:  #not include the start node's cost which is 0
        totalCost += node.pathCost - node.parent.pathCost  # cost of the step only
        node = node.parent
    return totalCost


def drawPath(ax, path, color = 'blue'):
    for i in range(len(path)-1):
        start = path[i]
        end  = path[i+1]
        ax.plot([start[0], end[0]],[start[1],end[1]], color = color)
        
        
def isPointInPoly(x, y, poly):
    num = len(poly)
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i].y > y) != (poly[j].y > y)) and \
                (x < (poly[j].x - poly[i].x) * (y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x):
            c = not c
        elif poly[i].y == poly[j].y and min(poly[i].x, poly[j].x) <= x <= max(poly[i].x, poly[j].x) and poly[i].y == y:
            c = True
            break
        elif poly[i].x == poly[j].x and min(poly[i].y, poly[j].y) <= y <= max(poly[i].y, poly[j].y) and poly[i].x == x:
            c = True
            break
        elif (poly[i].x, poly[i].y) == (x, y):
            c = True
            break
        elif (poly[i].y < y < poly[j].y or poly[i].y > y > poly[j].y) and \
             (poly[i].x < x < poly[j].x or poly[i].x > x > poly[j].x) and \
             ((poly[j].y - poly[i].y) * (x - poly[i].x) == (y - poly[i].y) * (poly[j].x - poly[i].x)):
            c = True
            break
        j = i
    return c

def markPolyAsObstacles(gridWidth, gridHeight, polygons):
    #marks all points inside polygons as obstacles.
    obstacles = set()
    for y in range(gridHeight):
        for x in range(gridWidth):
            for poly in polygons:
                if isPointInPoly(x, y, poly):
                    obstacles.add((x, y))
                    break
    return obstacles


if __name__ == "__main__":
    epolygons = gen_polygons('TestingGrid/world1_enclosures.txt')
    tpolygons = gen_polygons('TestingGrid/world1_turfs.txt')

    source = Point(8, 10)
    dest = Point(43, 45)

    gridWidth = 50
    gridHeight = 50
    obstacles = markPolyAsObstacles(gridWidth, gridHeight, epolygons)

    # dict for names in functs
    searchAlgorithms = {
        1: dfs,
        2: bfs,
        3: greedyBestFirstSearch,
        4: aStar
    }
    
    # what they represent in console to the user
    algoNames = {
        1: 'DFS',
        2: 'BFS',
        3: 'Greedy Best First Search',
        4: 'A*'
    }

    # diff colors for the diff algos
    colors = {
        1: 'blue',
        2: 'green',
        3: 'red',
        4: 'purple'
    }

    path_costs = {}


    # note there is a provided summary of the path cost (a* is very wrong!!) and it will also print to console
    
    while True:
        # untouched code provided from professor
        fig, ax = draw_board()
        draw_grids(ax)
        draw_source(ax, source.x, source.y)
        draw_dest(ax, dest.x, dest.y)

        for polygon in epolygons:
            for p in polygon:
                draw_point(ax, p.x, p.y)
            for i in range(len(polygon)):
                draw_line(ax, [polygon[i].x, polygon[(i + 1) % len(polygon)].x], [polygon[i].y, polygon[(i + 1) % len(polygon)].y])

        for polygon in tpolygons:
            for p in polygon:
                draw_green_point(ax, p.x, p.y)
            for i in range(len(polygon)):
                draw_green_line(ax, [polygon[i].x, polygon[(i + 1) % len(polygon)].x], [polygon[i].y, polygon[(i + 1) % len(polygon)].y])

        print("\nselect the search algorithm:")
        for key, value in algoNames.items():
            print(f"{key}: {value}")
        print("5:  to quit")

        choice = input("enter your choice (1-4) or 5 to quit: ").strip()

        if choice == '5':
            # when 5 is pressed then summary will populate with the algos you have decided to run
            # write the summary to a file before exiting
            with open('summary.txt', 'w') as file:
                for algo in algoNames:
                    cost = path_costs.get(algoNames[algo], "No path found")
                    file.write(f"{algoNames[algo]}: {cost}\n")
            print("exiting the program.")
            break

        try:
            # each function runs through here when called upon by its numeric value
            choice = int(choice)
            if choice in searchAlgorithms:
                problem = Problem(source.to_tuple(), dest.to_tuple(), gridWidth, gridHeight, obstacles, tpolygons)
                result = searchAlgorithms[choice](problem)
                if result is not None:
                    path = backtrackPath(result)
                    pathCost = totalPathCost(result)
                    path_costs[algoNames[choice]] = pathCost  # Store the path cost
                    print(f"path found with cost: {pathCost}")
                    drawPath(ax, path, colors[choice])
                    plt.show()
                else:
                    print(f"no path found using {algoNames[choice]}")
                    path_costs[algoNames[choice]] = "no path found"
            else:
                print("thats not a number between 1-5! please enter a number between 1-4 or 5 to quit")
        except ValueError:
            print("no letters! give me numbers please enter a number between 1-4 or 5 to quit")
