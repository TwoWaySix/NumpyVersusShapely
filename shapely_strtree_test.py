import time
import random
import math

import numpy as np
from shapely.strtree import STRtree
from shapely.geometry import Point, Polygon
from shapely.prepared import prep

from cythonloops.cython_loops import cy_assign_polyid


X_MIN, X_MAX, Y_MIN, Y_MAX = 0, 1000, 0, 1000

def create_random_points(n_points):
    points = [Point(random.randint(X_MIN, X_MAX), random.randint(X_MIN, X_MAX), index) for index in range(n_points)]
    print(f"\nCreated {n_points} Points.")
    return points


def create_random_polygons(n_polygons, n_verts, radius):
    d_angle = 2*math.pi / n_verts
    polygons = []
    for i in range(n_polygons):
        centroid = (random.randint(X_MIN, X_MAX), random.randint(Y_MIN, Y_MAX))
        points = []
        for vi in range(n_verts):
            phi = vi * d_angle
            x = radius*math.cos(phi) + centroid[0]
            y = radius*math.sin(phi) + centroid[1]
            points.append([x, y])
        polygons.append(Polygon(points))
    print(f"\nCreated {n_polygons} Polygons.")
    return polygons


def check_points_in_poly_with_pointtree(points, polygons):
    print("\nChecking points in polygon with a point based strtree")
    points_assigned_poly = np.zeros(len(points), dtype=int) - 1
    t0 = time.time()
    tree = STRtree(points)
    t1 = time.time()
    for pid, poly in enumerate(polygons):
        query_results = [pnt for pnt in tree.query(poly) if pnt.intersects(poly)]
        for pnt in query_results:
            points_assigned_poly[int(pnt.z)] = pid
    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")


def check_points_in_prepped_poly_with_pointtree_and_broadcasting(points, polygons):
    print("\nChecking points in PREPPED polygon with a point based strtree using numpy broadcasting")
    index_by_id = dict((id(pt), i) for i, pt in enumerate(points))
    points_assigned_poly = np.zeros(len(points), dtype=int) - 1
    t0 = time.time()
    tree = STRtree(points)
    t1 = time.time()
    for pid, poly in enumerate(polygons):
        prepped_poly = prep(poly)
        query_point_ids = [index_by_id[id(pnt)] for pnt in tree.query(poly) if prepped_poly.intersects(pnt)]
        points_assigned_poly[query_point_ids] = pid
        
    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")


def check_points_in_prepped_poly_with_pointtree_and_cythonforloop(points, polygons):
    print("\nChecking points in PREPPED polygon with a point based strtree and a cython for loop.")
    points_assigned_poly = np.zeros(len(points), dtype=int) - 1
    index_by_id = dict((id(pt), i) for i, pt in enumerate(points))
    t0 = time.time()
    tree = STRtree(points)
    t1 = time.time()
    for pid, poly in enumerate(polygons):
        prepped_poly = prep(poly)
        query_point_ids = np.array([index_by_id[id(pnt)] for pnt in tree.query(poly) if prepped_poly.intersects(pnt)], dtype=int)
        cy_assign_polyid(query_point_ids, points_assigned_poly, pid)
        
    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")


def check_points_in_prepped_poly_with_pointtree(points, polygons):
    print("\nChecking points in PREPPED polygon with a point based strtree.")
    index_by_id = dict((id(pt), i) for i, pt in enumerate(points))
    points_assigned_poly = [-1 for i in range(len(points))]
    t0 = time.time()
    tree = STRtree(points)
    t1 = time.time()
    for pid, poly in enumerate(polygons):
        prepped_poly = prep(poly)
        query_point_ids = [index_by_id[id(pnt)] for pnt in tree.query(poly) if prepped_poly.intersects(pnt)]
        for pntid in query_point_ids:
            points_assigned_poly[pntid] = pid
        
    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")



def check_points_in_prepped_poly_with_pointtree_and_filter(points, polygons):
    print("\nChecking points in PREPPED polygon with a point based strtree using filter")
    index_by_id = dict((id(pt), i) for i, pt in enumerate(points))
    points_assigned_poly = np.zeros(len(points), dtype=int) - 1
    # points_assigned_poly = [-1 for i in range(len(points))]
    t0 = time.time()
    tree = STRtree(points)
    # polygons = [prep(poly) for poly in _polygons]
    t1 = time.time()
    for pid, poly in enumerate(polygons):
        prepped_poly = prep(poly)
        query_points = tree.query(poly)
        hits = filter(prepped_poly.intersects, query_points) # TODO: THIS IS AMAAAZINGLY FAST
        for pnt in hits:
            points_assigned_poly[index_by_id[id(pnt)]] = pid # TODO: WHY THE HECK DOES THIS LOOP CAUSE IT TO BE SO SLOW?
        
    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")


def check_points_in_prepped_poly(points, polygons):
    print("\nChecking points in prepped polygon")
    points_assigned_poly = np.zeros(len(points), dtype=int) - 1
    t0 = time.time()
    for pid, poly in enumerate(polygons):
        prepped_poly = prep(poly)
        hits = filter(prepped_poly.intersects, points)
        for pnt in hits:
            points_assigned_poly[int(pnt.z)] = pid

    t1 = time.time()
    print(f"- It took {t1-t0:.2f} seconds for point in poly.")


def check_points_in_poly(points, polygons):
    print("\nChecking points in polygon")
    points_assigned_poly = np.zeros(len(points), dtype=int) - 1
    t0 = time.time()
    for pid, poly in enumerate(polygons):
        hits = filter(poly.intersects, points)
        for pnt in hits:
            points_assigned_poly[int(pnt.z)] = pid

    t1 = time.time()
    print(f"- It took {t1-t0:.2f} seconds for point in poly.")


def check_points_in_poly_with_polytree(points, polygons):
    print("\nChecking points in polygon with a polygon based strtree")
    points_assigned_poly = np.zeros(len(points), dtype=int) - 1
    t0 = time.time()
    tree = STRtree(polygons)
    t1 = time.time()
    for pnt in points:
        query_results = [poly for poly in tree.query(pnt) if pnt.intersects(poly)]
        # pid missing
        pid = -9999 # TODO
        points_assigned_poly[int(pnt.z)] = pid
        continue

    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")


def main():
    n_polygon_vertices = 50
    polygon_radius = 100
    
    # Version with lots of points and not so many polygons
    n_points = 500000
    n_polygons = 100
    # Creating geometry
    points = create_random_points(n_points)
    polygons = create_random_polygons(n_polygons, n_polygon_vertices, polygon_radius)
    # STRtree of points
    # check_points_in_poly_with_pointtree(points, polygons)
    check_points_in_prepped_poly_with_pointtree_and_cythonforloop(points, polygons)
    check_points_in_prepped_poly_with_pointtree_and_filter(points, polygons)
    check_points_in_prepped_poly_with_pointtree_and_broadcasting(points, polygons)
    check_points_in_prepped_poly_with_pointtree(points, polygons)
    # check_points_in_prepped_poly(points, polygons)
    # check_points_in_poly(points, polygons)
    # check_points_in_poly_with_polytree(points, polygons)


if __name__ == "__main__":
    main()

