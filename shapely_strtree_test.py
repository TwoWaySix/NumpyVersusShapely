import time
import random
import math

from shapely.strtree import STRtree
from shapely.geometry import Point, Polygon

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
    t0 = time.time()
    tree = STRtree(points)
    t1 = time.time()
    for poly in polygons:
        query_results = [pnt for pnt in tree.query(poly) if pnt.intersects(poly)]
    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")


def check_points_in_poly_with_polytree(points, polygons):
    print("\nChecking points in polygon with a polygon based strtree")
    t0 = time.time()
    tree = STRtree(polygons)
    t1 = time.time()
    for pnt in points:
        query_results = [poly for poly in tree.query(pnt) if pnt.intersects(poly)]
    t2 = time.time()
    print(f"- It took {t1-t0:.2f} seconds to build the tree.")
    print(f"- It took {t2-t1:.2f} seconds to query the tree.")


def main():
    n_polygon_vertices = 50
    polygon_radius = 100
    
    # Version with lots of points and not so many polygons
    n_points = 1000000
    n_polygons = 100
    # Creating geometry
    points = create_random_points(n_points)
    polygons = create_random_polygons(n_polygons, n_polygon_vertices, polygon_radius)
    # STRtree of points
    check_points_in_poly_with_pointtree(points, polygons)
    check_points_in_poly_with_polytree(points, polygons)


if __name__ == "__main__":
    main()

