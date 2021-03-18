import time
import random
import math

import numpy as np
from shapely.strtree import STRtree
from shapely.geometry import Point, Polygon
import shapefile

from cythonfunctions.cython_geometry import assign_points_to_polygons


X_MIN, X_MAX, Y_MIN, Y_MAX = 0, 1000, 0, 1000

def create_random_points(n_points):
    points = [(random.randint(X_MIN, X_MAX), random.randint(X_MIN, X_MAX), index) for index in range(n_points)]
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
        polygons.append(points)
    print(f"\nCreated {n_polygons} Polygons.")
    return polygons


def check_points_in_poly_shapely(_points, _polygons):
    points_conn_polygons = np.zeros(len(_points), dtype=int)
    t0 = time.time()
    print("\nCreating point geometries...")
    points = [Point(p) for p in _points]
    t1 = time.time()
    print("\nCreating polygon geometries...")
    polygons = [Polygon(poly) for poly in _polygons]

    print("\nChecking points in polygon with a polygon based strtree")
    t2 = time.time()
    tree = STRtree(polygons)
    t3 = time.time()
    for i, pnt in enumerate(points):
        query_results = [poly for poly in tree.query(pnt) if pnt.intersects(poly)]
        points_conn_polygons[i] = -9999

    t4 = time.time()
    print(f"- It took {t1-t0:.5f} seconds to create the point geometries.")
    print(f"- It took {t2-t1:.5f} seconds to create the polygon geometries.")
    print(f"- It took {t3-t2:.5f} seconds to build the tree.")
    print(f"- It took {t4-t3:.5f} seconds to query the tree.")
    return points_conn_polygons


def create_polygon_bboxes(polygons):
    polygon_bboxes = np.zeros((len(polygons), 4))
    for i in range(polygon_bboxes.shape[0]):
        poly = np.array(polygons[i])
        mins = poly.min(axis=0) 
        maxs = poly.max(axis=0) 
        polygon_bboxes[i, 0] = mins[0]
        polygon_bboxes[i, 2] = mins[1]
        polygon_bboxes[i, 1] = maxs[0]
        polygon_bboxes[i, 3] = maxs[1]
    return polygon_bboxes


def check_points_in_poly_cython(_points, _polygons, radius):
    t0 = time.time()
    points = np.array(_points, dtype=float)
    polygons = [np.array(poly) for poly in _polygons]
    t1 = time.time()
    polygon_bboxes = create_polygon_bboxes(polygons)
    t2 = time.time()
    points_conn_polygons = np.zeros((points.shape[0]), dtype=int)
    assign_points_to_polygons(points, polygons, points_conn_polygons, polygon_bboxes, ray_length=10*radius)
    t3 = time.time()
    print(f"- It took {t1-t0:.5f} seconds to create the numpy points array.")
    print(f"- It took {t2-t1:.5f} seconds to create the polygon bounding boxes.")
    print(f"- It took {t3-t2:.5f} seconds to do the point in poly.")
    return points_conn_polygons
     

def write_polygons_to_shapefile(polygons, path):
    w = shapefile.Writer(path)
    w.field("poly_id", "N")

    for i, points in enumerate(polygons):
        w.record(i)
        w.poly([points])
    w.close()


def write_points_to_shapefile(points, points_conn_polygons, path):
    w = shapefile.Writer(path)
    w.field("poly_id", "N")

    for i, pnt in enumerate(points):
        w.record(points_conn_polygons[i])
        w.point(pnt[0], pnt[1])
    w.close()



def main():
    n_polygon_vertices = 50
    polygon_radius = 30
    
    # Version with lots of points and not so many polygons
    n_points = 400000
    n_polygons = 100
    # Creating geometry
    points = create_random_points(n_points)
    polygons = create_random_polygons(n_polygons, n_polygon_vertices, polygon_radius)
    write_polygons_to_shapefile(polygons, "results/polygons.shp")
    
    # STRtree of points
    print("\n\nSHAPELY")
    points_conn_polygons_shapely = check_points_in_poly_shapely(points, polygons)

    print("\n\nCYTHON")
    points_conn_polygons_cython = check_points_in_poly_cython(points, polygons, polygon_radius)

    print("\n\nWriting results to shapefiles...")
    write_points_to_shapefile(points, points_conn_polygons_cython, "results/points_cython.shp")


if __name__ == "__main__":
    main()
