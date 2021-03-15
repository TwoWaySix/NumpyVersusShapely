import time
import random

import numpy as np
from shapely.geometry import Point, Polygon


n_nodes = 1000
n_elements = 10000

nodes_list = [[random.random(), random.random()] for i in range(n_nodes)]
elements_list = [[random.randint(0, n_nodes - 1), 
                  random.randint(0, n_nodes - 1), 
                  random.randint(0, n_nodes - 1)] 
                  for i in range(n_elements)] 


def centroids_shapely():
    print("\nUsing shapely")
    t0 = time.time()
    print("- Creating nodes as Points...")
    nodes_shapely = [Point(x, y) for x, y in nodes_list]
    t1 = time.time()
    print("- Creating elements as Polygons...")
    elements_shapely = [Polygon((nodes_shapely[nid1],
                                nodes_shapely[nid2],
                                nodes_shapely[nid3]))
                                for nid1, nid2, nid3 in elements_list]
    t2 = time.time()
    print("- Calculating element centroids...")
    element_centroids = [elmt.centroid for elmt in elements_shapely]
    t3 = time.time()
    dt_shapely = t3 - t0
    print(f"Finished after {dt_shapely:.2f} seconds")
    print(f"{t1-t0:.3f} // {t2-t1:.3f} // {t3-t2:.3f}")

    return element_centroids


def centroids_numpy():
    print("\nUsing numpy")
    t0 = time.time()
    print("- Creating nodes as array...")
    nodes_np = np.array(nodes_list)
    t1 = time.time()
    print("- Creating elements as array...")
    elements_np = np.array(elements_list, dtype=np.int32)
    t2 = time.time()
    print("- Calculating element centroids...")
    element_centroids = nodes_np[elements_np].mean(axis=1)
    t3 = time.time()
    dt_np = t3 - t0
    print(f"Finished after {dt_np:.2f} seconds")
    print(f"{t1-t0:.3f} // {t2-t1:.3f} // {t3-t2:.3f}")

    return element_centroids


def test_centroids_shapely(benchmark):
    centroids = benchmark(centroids_shapely)
    assert centroids != None


def test_centroids_numpy(benchmark):
    centroids = benchmark(centroids_numpy)
    assert centroids.any() != None
