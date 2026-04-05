"""
benchmark.py — Run DFS, BFS, UCS across multiple mazes and print a comparison table.
Usage: python benchmark.py
"""

import subprocess
import re
import sys

ALGORITHMS = ["dfs", "bfs", "ucs"]
MAZES = ["tinyMaze", "mediumMaze", "bigMaze"]

def run(maze, algorithm):
    cmd = [
        sys.executable, "pacman.py",
        "-l", maze,
        "-p", "SearchAgent",
        "-a", f"fn={algorithm}",
        "--frameTime", "-1",
        "-q"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    return output

def parse(output):
    data = {
        "cost":     None,
        "nodes":    None,
        "time":     None,
        "score":    None,
        "result":   "FAIL",
    }
    m = re.search(r"Path found with total cost of (\d+) in ([\d.]+) seconds", output)
    if m:
        data["cost"] = int(m.group(1))
        data["time"] = float(m.group(2))

    m = re.search(r"Search nodes expanded: (\d+)", output)
    if m:
        data["nodes"] = int(m.group(1))

    m = re.search(r"Average Score:\s+([\d.]+)", output)
    if m:
        data["score"] = float(m.group(1))

    if "victorious" in output:
        data["result"] = "WIN"

    return data

def col(value, width):
    return str(value if value is not None else "N/A").center(width)

def main():
    results = {}
    print("Running benchmarks...\n")
    for maze in MAZES:
        for algo in ALGORITHMS:
            key = (maze, algo)
            print(f"  {algo.upper():3s} on {maze}...", end=" ", flush=True)
            output = run(maze, algo)
            results[key] = parse(output)
            d = results[key]
            print(f"cost={d['cost']}, nodes={d['nodes']}, time={d['time']}s")

    # --- Print table ---
    print()
    header_cols = ["Maze", "Algorithm", "Result", "Path Cost", "Nodes Expanded", "Time (s)", "Score"]
    widths      = [14,      11,          8,         10,          16,               10,         7]

    sep = "+" + "+".join("-" * w for w in widths) + "+"
    header = "|" + "|".join(h.center(w) for h, w in zip(header_cols, widths)) + "|"

    print(sep)
    print(header)
    print(sep)

    for maze in MAZES:
        for algo in ALGORITHMS:
            d = results[(maze, algo)]
            row = [
                col(maze,         widths[0]),
                col(algo.upper(), widths[1]),
                col(d["result"],  widths[2]),
                col(d["cost"],    widths[3]),
                col(d["nodes"],   widths[4]),
                col(d["time"],    widths[5]),
                col(d["score"],   widths[6]),
            ]
            print("|" + "|".join(row) + "|")
        print(sep)

    # --- Observations ---
    print("\nObservations:")
    for maze in MAZES:
        dfs  = results[(maze, "dfs")]
        bfs  = results[(maze, "bfs")]
        ucs  = results[(maze, "ucs")]
        print(f"\n  {maze}:")
        if bfs["cost"] and dfs["cost"]:
            optimal = "BFS/UCS" if bfs["cost"] <= dfs["cost"] else "DFS"
            print(f"    Shortest path : {optimal} (BFS={bfs['cost']}, UCS={ucs['cost']}, DFS={dfs['cost']})")
        if bfs["nodes"] and dfs["nodes"]:
            fewest = min(["dfs","bfs","ucs"], key=lambda a: results[(maze,a)]["nodes"] or 9999)
            print(f"    Fewest nodes  : {fewest.upper()} ({results[(maze,fewest)]['nodes']} expanded)")

if __name__ == "__main__":
    main()
