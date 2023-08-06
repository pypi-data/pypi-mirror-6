'''
Venn diagram plotting routines.
Three-circle venn plotter.

Copyright 2012, Konstantin Tretyakov.
http://kt.era.ee/

Licensed under MIT license.
'''
import numpy as np
import warnings

from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path
from matplotlib.colors import ColorConverter
from matplotlib.pyplot import gca

from matplotlib_venn._math import *
from matplotlib_venn._common import *

def compute_venn3_areas(diagram_areas, normalize_to=1.0, _minimal_area=1e-6):
    '''
    The list of venn areas is given as 7 values, corresponding to venn diagram areas in the following order:
     (Abc, aBc, ABc, abC, AbC, aBC, ABC)
    (i.e. last element corresponds to the size of intersection A&B&C).
    The return value is a list of areas (A_a, A_b, A_c, A_ab, A_bc, A_ac, A_abc),
    such that the total area of all circles is normalized to normalize_to. 
    If the area of any circle is smaller than _minimal_area, makes it equal to _minimal_area.

    Assumes all input values are nonnegative (to be more precise, all areas are passed through and abs() function)
    >>> compute_venn3_areas((1, 1, 0, 1, 0, 0, 0))
    (0.33..., 0.33..., 0.33..., 0.0, 0.0, 0.0, 0.0)
    >>> compute_venn3_areas((0, 0, 0, 0, 0, 0, 0))
    (1e-06, 1e-06, 1e-06, 0.0, 0.0, 0.0, 0.0)
    >>> compute_venn3_areas((1, 1, 1, 1, 1, 1, 1), normalize_to=7)
    (4.0, 4.0, 4.0, 2.0, 2.0, 2.0, 1.0)
    >>> compute_venn3_areas((1, 2, 3, 4, 5, 6, 7), normalize_to=56/2)
    (16.0, 18.0, 22.0, 10.0, 13.0, 12.0, 7.0)
    '''
    # Normalize input values to sum to 1
    areas = np.array(np.abs(diagram_areas), float)
    total_area = np.sum(areas)
    if np.abs(total_area) < _minimal_area:
        warnings.warn("All circles have zero area")
        return (1e-06, 1e-06, 1e-06, 0.0, 0.0, 0.0, 0.0)
    else:
        areas = areas / total_area * normalize_to
        A_a = areas[0] + areas[2] + areas[4] + areas[6]
        if A_a < _minimal_area:
            warnings.warn("Circle A has zero area")
            A_a = _minimal_area
        A_b = areas[1] + areas[2] + areas[5] + areas[6]
        if A_b < _minimal_area:
            warnings.warn("Circle B has zero area")
            A_b = _minimal_area
        A_c = areas[3] + areas[4] + areas[5] + areas[6]
        if A_c < _minimal_area:
            warnings.warn("Circle C has zero area")
            A_c = _minimal_area

        # Areas of the three intersections (ab, ac, bc)
        A_ab, A_ac, A_bc = areas[2] + areas[6], areas[4] + areas[6], areas[5] + areas[6]

        return (A_a, A_b, A_c, A_ab, A_bc, A_ac, areas[6])


def solve_venn3_circles(venn_areas):
    '''
    Given the list of "venn areas" (as output from compute_venn3_areas, i.e. [A, B, C, AB, BC, AC, ABC]),
    finds the positions and radii of the three circles.
    The return value is a tuple (coords, radii), where coords is a 3x2 array of coordinates and
    radii is a 3x1 array of circle radii.

    Assumes the input values to be nonnegative and not all zero.
    In particular, the first three values must all be positive.

    The overall match is only approximate (to be precise, what is matched are the areas of the circles and the
    three pairwise intersections).

    >>> c, r = solve_venn3_circles((1, 1, 1, 0, 0, 0, 0))
    >>> np.round(r, 3)
    array([ 0.564,  0.564,  0.564])
    >>> c, r = solve_venn3_circles(compute_venn3_areas((1, 2, 40, 30, 4, 40, 4)))
    >>> np.round(r, 3)
    array([ 0.359,  0.476,  0.453])
    '''
    (A_a, A_b, A_c, A_ab, A_bc, A_ac, A_abc) = list(map(float, venn_areas))
    r_a, r_b, r_c = np.sqrt(A_a / np.pi), np.sqrt(A_b / np.pi), np.sqrt(A_c / np.pi)
    intersection_areas = [A_ab, A_bc, A_ac]
    radii = np.array([r_a, r_b, r_c])

    # Hypothetical distances between circle centers that assure
    # that their pairwise intersection areas match the requirements.
    dists = [find_distance_by_area(radii[i], radii[j], intersection_areas[i]) for (i, j) in [(0, 1), (1, 2), (2, 0)]]

    # How many intersections have nonzero area?
    num_nonzero = sum(np.array([A_ab, A_bc, A_ac]) > tol)

    # Handle four separate cases:
    #    1. All pairwise areas nonzero
    #    2. Two pairwise areas nonzero
    #    3. One pairwise area nonzero
    #    4. All pairwise areas zero.

    if num_nonzero == 3:
        # The "generic" case, simply use dists to position circles at the vertices of a triangle.
        # Before we need to ensure that resulting circles can be at all positioned on a triangle,
        # use an ad-hoc fix.
        for i in range(3):
            i, j, k = (i, (i + 1) % 3, (i + 2) % 3)
            if dists[i] > dists[j] + dists[k]:
                dists[i] = 0.8 * (dists[j] + dists[k])
                warnings.warn("Bad circle positioning")
        coords = position_venn3_circles_generic(radii, dists)
    elif num_nonzero == 2:
        # One pair of circles is not intersecting.
        # In this case we can position all three circles in a line
        # The two circles that have no intersection will be on either sides.
        for i in range(3):
            if intersection_areas[i] < tol:
                (left, right, middle) = (i, (i + 1) % 3, (i + 2) % 3)
                coords = np.zeros((3, 2))
                coords[middle][0] = dists[middle]
                coords[right][0] = dists[middle] + dists[right]
                # We want to avoid the situation where left & right still intersect
                if coords[left][0] + radii[left] > coords[right][0] - radii[right]:
                    mid = (coords[left][0] + radii[left] + coords[right][0] - radii[right]) / 2.0
                    coords[left][0] = mid - radii[left] - 1e-5
                    coords[right][0] = mid + radii[right] + 1e-5
                break
    elif num_nonzero == 1:
        # Only one pair of circles is intersecting, and one circle is independent.
        # Position all on a line first two intersecting, then the free one.
        for i in range(3):
            if intersection_areas[i] > tol:
                (left, right, side) = (i, (i + 1) % 3, (i + 2) % 3)
                coords = np.zeros((3, 2))
                coords[right][0] = dists[left]
                coords[side][0] = dists[left] + radii[right] + radii[side] * 1.1  # Pad by 10%
                break
    else:
        # All circles are non-touching. Put them all in a sequence
        coords = np.zeros((3, 2))
        coords[1][0] = radii[0] + radii[1] * 1.1
        coords[2][0] = radii[0] + radii[1] * 1.1 + radii[1] + radii[2] * 1.1

    coords = normalize_by_center_of_mass(coords, radii)
    return (coords, radii)


def position_venn3_circles_generic(radii, dists):
    '''
    Given radii = (r_a, r_b, r_c) and distances between the circles = (d_ab, d_bc, d_ac),
    finds the coordinates of the centers for the three circles so that they form a proper triangle.
    The current positioning method puts the center of A and B on a horizontal line y==0,
    and C just below.

    Returns a 3x2 array with circle center coordinates in rows.

    >>> position_venn3_circles_generic((1, 1, 1), (0, 0, 0))
    array([[ 0.,  0.],
           [ 0.,  0.],
           [ 0., -0.]])
    >>> position_venn3_circles_generic((1, 1, 1), (2, 2, 2))
    array([[ 0.        ,  0.        ],
           [ 2.        ,  0.        ],
           [ 1.        , -1.73205081]])
    '''
    (d_ab, d_bc, d_ac) = dists
    (r_a, r_b, r_c) = radii
    coords = np.array([[0, 0], [d_ab, 0], [0, 0]], float)
    C_x = (d_ac**2 - d_bc**2 + d_ab**2) / 2.0 / d_ab if np.abs(d_ab) > tol else 0.0
    C_y = -np.sqrt(d_ac**2 - C_x**2)
    coords[2, :] = C_x, C_y
    return coords


def compute_venn3_regions(centers, radii):
    '''
    Given the 3x2 matrix with circle center coordinates, and a 3-element list (or array) with circle radii [as returned from solve_venn3_circles],
    returns the 7 regions, comprising the venn diagram.
    Each region is given as [array([pt_1, pt_2, pt_3]), (arc_1, arc_2, arc_3), label_pos] where each pt_i gives the coordinates of a point,
    and each arc_i is in turn a triple (circle_center, circle_radius, direction), and label_pos is the recommended center point for
    positioning region label.

    The region is the poly-curve constructed by moving from pt_1 to pt_2 along arc_1, then to pt_3 along arc_2 and back to pt_1 along arc_3.
    Arc direction==True denotes positive (CCW) direction.

     There is also a special case, where the region is given as
    ["CIRCLE", (center, radius, True), label_pos], which corresponds to a completely circular region.

    Regions are returned in order (Abc, aBc, ABc, abC, AbC, aBC, ABC)

    >>> centers, radii = solve_venn3_circles((1, 1, 1, 1, 1, 1, 1))
    >>> regions = compute_venn3_regions(centers, radii)
    '''
    #(a, b, c) = (0, 1, 2)  <- This makes it possible to use the same code for the three regions aBC, AbC, ABc

    # This is the floating point comparison tolerance that we use when checking whether a circle is inside another one
    # The value is due to the default "numeric_correction" parameter used in _math.find_distance_by_area()
    VISUAL_TOLERANCE = 1e-04 + tol    
    
    # Internal function to check whether one circle is completely within another. Circles given as their ids [0,1,2]
    def circle_inside(i, j): # Returns True if circle i is inside circle j
        return np.linalg.norm(centers[i] - centers[j]) + radii[i] <= radii[j] + VISUAL_TOLERANCE
        
    # First compute all pairwise circle intersections
    intersections = [circle_circle_intersection(centers[i], radii[i], centers[j], radii[j]) for (i, j) in [(0, 1), (1, 2), (2, 0)]]
    regions = []
    
    # Regions [Abc, aBc, abC]
    for i in range(3):
        (a, b, c) = (i, (i + 1) % 3, (i + 2) % 3)
        
        # (Issue 10) First check whether A is fully inside B or inside C. In this case the region is empty.
        if np.linalg.norm(centers[b] - centers[a]) + radii[a] <= radii[b] + VISUAL_TOLERANCE:  # A is totally within B
            regions.append(None)
            continue
        elif np.linalg.norm(centers[c] - centers[a]) + radii[a] <= radii[c] + VISUAL_TOLERANCE:  # A is totally within C
            regions.append(None)
            continue
        
        if intersections[a] is not None and intersections[c] is not None:
            # Current circle intersects both of the other circles.
            if intersections[b] is not None:
                # .. and the two other circles intersect, this is either the "normal" situation
                #    or it can also be a case of bad placement
                if np.linalg.norm(intersections[b][0] - centers[a]) < radii[a]:
                    # In the "normal" situation we use the scheme [(BA, B+), (BC, C+), (AC, A-)]
                    points = np.array([intersections[a][1], intersections[b][0], intersections[c][1]])
                    arcs = [(centers[b], radii[b], True), (centers[c], radii[c], True), (centers[a], radii[a], False)]

                    # Ad-hoc label positioning
                    pt_a = intersections[b][0]
                    pt_b = intersections[b][1]
                    pt_c = circle_line_intersection(centers[a], radii[a], pt_a, pt_b)
                    if pt_c is None:
                        label_pos = circle_circle_intersection(centers[b], radii[b] + 0.1 * radii[a], centers[c], radii[c] + 0.1 * radii[c])[0]
                    else:
                        label_pos = 0.5 * (pt_c[1] + pt_a)
                else:
                    # This is the "bad" situation (basically one disc covers two touching disks)
                    # We use the scheme [(BA, B+), (AB, A-)] if (AC is inside B) and
                    #                   [(CA, C+), (AC, A-)] otherwise
                    if np.linalg.norm(intersections[c][0] - centers[b]) < radii[b]:
                        points = np.array([intersections[a][1], intersections[a][0]])
                        arcs = [(centers[b], radii[b], True), (centers[a], radii[a], False)]
                    else:
                        points = np.array([intersections[c][0], intersections[c][1]])
                        arcs = [(centers[c], radii[c], True), (centers[a], radii[a], False)]
                    label_pos = centers[a]
            else:
                # .. and the two other circles do not intersect. This means we are in the "middle" of a OoO placement.
                # The patch is then a [(AB, B-), (BA, A+), (AC, C-), (CA, A+)]
                points = np.array([intersections[a][0], intersections[a][1], intersections[c][1], intersections[c][0]])
                arcs = [(centers[b], radii[b], False), (centers[a], radii[a], True), (centers[c], radii[c], False), (centers[a], radii[a], True)]
                # Label will be between the b and c circles
                leftc, rightc = (b, c) if centers[b][0] < centers[c][0] else (c, b)
                label_x = ((centers[leftc][0] + radii[leftc]) + (centers[rightc][0] - radii[rightc])) / 2.0
                label_y = centers[a][1] + radii[a] / 2.0
                label_pos = np.array([label_x, label_y])
        elif intersections[a] is None and intersections[c] is None:
            # Current circle is completely separate from others
            points = "CIRCLE"
            arcs = (centers[a], radii[a], True)
            label_pos = centers[a]
        else:
            # Current circle intersects one of the other circles
            other_circle = b if intersections[a] is not None else c
            other_circle_intersection = a if intersections[a] is not None else c
            i1, i2 = (0, 1) if intersections[a] is not None else (1, 0)
            # The patch is a [(AX, A-), (XA, X+)]
            points = np.array([intersections[other_circle_intersection][i1], intersections[other_circle_intersection][i2]])
            arcs = [(centers[a], radii[a], False), (centers[other_circle], radii[other_circle], True)]
            if centers[a][0] < centers[other_circle][0]:
                # We are to the left
                label_pos_x = (centers[a][0] - radii[a] + centers[other_circle][0] - radii[other_circle]) / 2.0
            else:
                # We are to the right
                label_pos_x = (centers[a][0] + radii[a] + centers[other_circle][0] + radii[other_circle]) / 2.0
            label_pos = np.array([label_pos_x, centers[a][1]])
        regions.append((points, arcs, label_pos))
    
    # In the following we shall need to know, whether there is a "middle" region.
    (a, b, c) = (0, 1, 2)
    has_middle_region = intersections[a] is not None and intersections[b] is not None and intersections[c] is not None and\
                        (np.linalg.norm(intersections[b][0] - centers[a]) < radii[a] or\
                        np.linalg.norm(intersections[c][0] - centers[b]) < radii[b] or\
                        np.linalg.norm(intersections[a][0] - centers[c]) < radii[c])
    
    # Regions [aBC, AbC, ABc]
    for i in range(3):
        (a, b, c) = (i, (i + 1) % 3, (i + 2) % 3)

        if intersections[b] is None:  # B and C do not intersect, no region there
            regions.append(None)
            continue
            
        # (Issue 10). There is a possibility, that the region aBC does not exist because B or C is completely within A.
        if circle_inside(b, a):
            regions.append(None)
            continue
        if circle_inside(c, a):  # C is totally within A
            regions.append(None)
            continue        

        # (Issue 10). Another inconvenient possibility is that B is totally within C, or C within B, in which case
        # the region aBC is basically aB or aC.
        if circle_inside(b, c):  
            # B is totally within C
            # Now if A and B intersect, the region is [(AB, A+), (BA, B-)]
            if intersections[a] is not None:
                points = np.array([intersections[a][0], intersections[a][1]])
                arcs = [(centers[a], radii[a], True), (centers[b], radii[b], False)]
                # Ad-hoc label positioning
                dir_a_to_b = centers[b] - centers[a]
                dir_a_to_b = dir_a_to_b / np.linalg.norm(dir_a_to_b)
                pt_a = centers[a] + radii[a]*dir_a_to_b
                pt_b = centers[a] + (radii[b] + np.linalg.norm(centers[b] - centers[a]))*dir_a_to_b
                label_pos = 0.5 * (pt_a + pt_b)
            else:
                # A and B do not intersect, the region is just the circle B
                points = "CIRCLE"
                arcs = (centers[b], radii[b], True)
                label_pos = centers[b]
            regions.append((points, arcs, label_pos))
            continue
        elif circle_inside(c, b): 
            # Same as above, but now C totally in B
            # Now if A and C intersect, the region is [(AC, A+), (CA, C-)]
            if intersections[c] is not None:
                points = np.array([intersections[c][1], intersections[c][0]])
                arcs = [(centers[a], radii[a], True), (centers[c], radii[c], False)]
                # Ad-hoc label positioning
                dir_a_to_c = centers[c] - centers[a]
                dir_a_to_c = dir_a_to_c / np.linalg.norm(dir_a_to_c)
                pt_a = centers[a] + radii[a]*dir_a_to_c
                pt_b = centers[a] + (radii[c] + np.linalg.norm(centers[c] - centers[a]))*dir_a_to_c
                label_pos = 0.5 * (pt_a + pt_b)
            else:
                # A and C do not intersect, the region is just the circle C
                points = "CIRCLE"
                arcs = (centers[c], radii[c], True)
                label_pos = centers[c]
            regions.append((points, arcs, label_pos))
            continue
        
        # The remaining options are as follows: either there is a "middle" triangular region ABC [the most common form of a Venn diagram],
        # or there is no such region, and BC is located completely outside of the circle A.
        if has_middle_region:
            # This is the "normal" situation (i.e. all three circles have a common area)
            # We then use the scheme [(CB, C+), (CA, A-), (AB, B+)]
            points = np.array([intersections[b][1], intersections[c][0], intersections[a][0]])
            arcs = [(centers[c], radii[c], True), (centers[a], radii[a], False), (centers[b], radii[b], True)]
            # Ad-hoc label positioning
            pt_a = intersections[b][1]
            dir_to_a = pt_a - centers[a]
            dir_to_a = dir_to_a / np.linalg.norm(dir_to_a)
            pt_b = centers[a] + dir_to_a * radii[a]
            label_pos = 0.5 * (pt_a + pt_b)
        else:
            # This is the situation, where there is no common area
            # Then the corresponding area is made by scheme [(CB, C+), (BC, B+), None]
            points = np.array([intersections[b][1], intersections[b][0]])
            arcs = [(centers[c], radii[c], True), (centers[b], radii[b], True)]
            label_pos = 0.5 * (intersections[b][1] + intersections[b][0])

        regions.append((points, arcs, label_pos))

    # Central region made by scheme [(BC, B+), (AB, A+), (CA, C+)], unless one of the circles is totally inside some other.
    (a, b, c) = (0, 1, 2)
    if intersections[a] is None or intersections[b] is None or intersections[c] is None:
        # No middle region
        regions.append(None)
    else:
        # Now check for a special case, where one of the circles is inside another
        done_last_region = False
        for i in range(3):
            (a, b, c) = (i, (i + 1) % 3, (i + 2) % 3)
            if circle_inside(a, b):
                # [(AC, A+), (CA, C+)]
                points = np.array([intersections[c][1], intersections[c][0]])
                label_pos = np.mean(points, 0)  # Middle of the central region
                arcs = [(centers[a], radii[a], True), (centers[c], radii[c], True)]
                regions.append((points, arcs, label_pos))
                done_last_region = True
                break
            elif circle_inside(a, c):
                # [(AB, A+), (BA, B+)]
                points = np.array([intersections[a][0], intersections[a][1]])
                label_pos = np.mean(points, 0)  # Middle of the central region
                arcs = [(centers[a], radii[a], True), (centers[b], radii[b], True)]
                regions.append((points, arcs, label_pos))
                done_last_region = True
                break                
        # No, the standard case
        if not done_last_region:
            # The standard case
            points = np.array([intersections[b][0], intersections[a][0], intersections[c][0]])
            label_pos = np.mean(points, 0)  # Middle of the central region
            arcs = [(centers[b], radii[b], True), (centers[a], radii[a], True), (centers[c], radii[c], True)]
            if has_middle_region:
                regions.append((points, arcs, label_pos))
            else:
                regions.append(([], [], label_pos))

    #      (Abc,        aBc,        ABc,        abC,        AbC,        aBC,        ABC)
    return (regions[0], regions[1], regions[5], regions[2], regions[4], regions[3], regions[6])


def make_venn3_region_patch(region):
    '''
    Given a venn3 region (as returned from compute_venn3_regions) produces a Patch object,
    depicting the region as a curve.

    >>> centers, radii = solve_venn3_circles((1, 1, 1, 1, 1, 1, 1))
    >>> regions = compute_venn3_regions(centers, radii)
    >>> patches = [make_venn3_region_patch(r) for r in regions]
    '''
    if region is None or len(region[0]) == 0:
        return None
    if region[0] == "CIRCLE":
        return Circle(region[1][0], region[1][1])
    pts, arcs, label_pos = region
    path = [pts[0]]
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        (center, radius, direction) = arcs[i]
        fromangle = vector_angle_in_degrees(pts[i] - center)
        toangle = vector_angle_in_degrees(pts[j] - center)
        if direction:
            vertices = Path.arc(fromangle, toangle).vertices
        else:
            vertices = Path.arc(toangle, fromangle).vertices
            vertices = vertices[np.arange(len(vertices) - 1, -1, -1)]
        vertices = vertices * radius + center
        path = path + list(vertices[1:])
    codes = [1] + [4] * (len(path) - 1)
    return PathPatch(Path(path, codes))


def compute_venn3_colors(set_colors):
    '''
    Given three base colors, computes combinations of colors corresponding to all regions of the venn diagram.
    returns a list of 7 elements, providing colors for regions (100, 010, 110, 001, 101, 011, 111).

    >>> compute_venn3_colors(['r', 'g', 'b'])
    (array([ 1.,  0.,  0.]),..., array([ 0.4,  0.2,  0.4]))
    '''
    ccv = ColorConverter()
    base_colors = [np.array(ccv.to_rgb(c)) for c in set_colors]
    return (base_colors[0], base_colors[1], mix_colors(base_colors[0], base_colors[1]), base_colors[2],
            mix_colors(base_colors[0], base_colors[2]), mix_colors(base_colors[1], base_colors[2]), mix_colors(base_colors[0], base_colors[1], base_colors[2]))


def compute_venn3_subsets(a, b, c):
	'''
	Given three set objects, computes the sizes of (a & ~b & ~c, ~a & b & ~c, a & b & ~c, ....), 
	as needed by the subsets parameter of venn3 and venn3_circles.
	Returns the result as a tuple.
	
	>>> compute_venn3_subsets(set([1,2,3]), set([2,3,4]), set([3,4,5,6]))
	(1, 0, 1, 2, 0, 1, 1)
	>>> compute_venn3_subsets(set([]), set([]), set([]))
	(0, 0, 0, 0, 0, 0, 0)
	>>> compute_venn3_subsets(set([1]), set([]), set([]))
	(1, 0, 0, 0, 0, 0, 0)
	>>> compute_venn3_subsets(set([]), set([1]), set([]))
	(0, 1, 0, 0, 0, 0, 0)
	>>> compute_venn3_subsets(set([]), set([]), set([1]))
	(0, 0, 0, 1, 0, 0, 0)
	>>> compute_venn3_subsets(set([1]), set([1]), set([1]))
	(0, 0, 0, 0, 0, 0, 1)
	>>> compute_venn3_subsets(set([1,3,5,7]), set([2,3,6,7]), set([4,5,6,7]))
	(1, 1, 1, 1, 1, 1, 1)
	'''
	return (len(a - (b.union(c))),  # TODO: This is certainly not the most efficient way to compute.
            len(b - (a.union(c))),
            len(a.intersection(b) - c),
            len(c - (a.union(b))),
            len(a.intersection(c) - b),
            len(b.intersection(c) - a),
            len(a.intersection(b).intersection(c)))


def venn3_circles(subsets, normalize_to=1.0, alpha=1.0, color='black', linestyle='solid', linewidth=2.0, ax=None, **kwargs):
    '''
    Plots only the three circles for the corresponding Venn diagram.
    Useful for debugging or enhancing the basic venn diagram.
    parameters ``subsets``, ``normalize_to`` and ``ax`` are the same as in venn3()
    kwargs are passed as-is to matplotlib.patches.Circle.
    returns a list of three Circle patches.

    >>> plot = venn3_circles({'001': 10, '100': 20, '010': 21, '110': 13, '011': 14})
	>>> plot = venn3_circles([set(['A','B','C']), set(['A','D','E','F']), set(['D','G','H'])])
    '''
    # Prepare parameters
    if isinstance(subsets, dict):
        subsets = [subsets.get(t, 0) for t in ['100', '010', '110', '001', '101', '011', '111']]
    elif len(subsets) == 3:
        subsets = compute_venn3_subsets(*subsets)
        
    areas = compute_venn3_areas(subsets, normalize_to)
    centers, radii = solve_venn3_circles(areas)
    
    if ax is None:
        ax = gca()
    prepare_venn_axes(ax, centers, radii)
    result = []
    for (c, r) in zip(centers, radii):
        circle = Circle(c, r, alpha=alpha, edgecolor=color, facecolor='none', linestyle=linestyle, linewidth=linewidth, **kwargs)
        ax.add_patch(circle)
        result.append(circle)
    return result


def venn3(subsets, set_labels=('A', 'B', 'C'), set_colors=('r', 'g', 'b'), alpha=0.4, normalize_to=1.0, ax=None):
    '''Plots a 3-set area-weighted Venn diagram.
    The subsets parameter can be one of the following:
	 - A list (or a tuple), containing three set objects.
     - A dict, providing sizes of seven diagram regions.
       The regions are identified via three-letter binary codes ('100', '010', etc), hence a valid set could look like:
       {'001': 10, '010': 20, '110':30, ...}. Unmentioned codes are considered to map to 0.
     - A list (or a tuple) with 7 numbers, denoting the sizes of the regions in the following order:
       (100, 010, 110, 001, 101, 011, 111).

    ``set_labels`` parameter is a list of three strings - set labels. Set it to None to disable set labels.
    The ``set_colors`` parameter should be a list of three elements, specifying the "base colors" of the three circles.
    The colors of circle intersections will be computed based on those.

    The ``normalize_to`` parameter specifies the total (on-axes) area of the circles to be drawn. Sometimes tuning it (together
    with the overall fiture size) may be useful to fit the text labels better.
    The return value is a ``VennDiagram`` object, that keeps references to the ``Text`` and ``Patch`` objects used on the plot
    and lets you know the centers and radii of the circles, if you need it.

    The ``ax`` parameter specifies the axes on which the plot will be drawn (None means current axes).

    Note: if some of the circles happen to have zero area, you will probably not get a nice picture.
    
    >>> import matplotlib # (The first two lines prevent the doctest from falling when TCL not installed. Not really necessary in most cases)
    >>> matplotlib.use('Agg')
    >>> from matplotlib_venn import *
    >>> v = venn3(subsets=(1, 1, 1, 1, 1, 1, 1), set_labels = ('A', 'B', 'C'))
    >>> c = venn3_circles(subsets=(1, 1, 1, 1, 1, 1, 1), linestyle='dashed')
    >>> v.get_patch_by_id('100').set_alpha(1.0)
    >>> v.get_patch_by_id('100').set_color('white')
    >>> v.get_label_by_id('100').set_text('Unknown')
    >>> v.get_label_by_id('C').set_text('Set C')
	
	You can provide sets themselves rather than subset sizes:
    >>> v = venn3(subsets=[set([1,2]), set([2,3,4,5]), set([4,5,6,7,8,9,10,11])])
    >>> print("%0.2f %0.2f %0.2f" % (v.get_circle_radius(0), v.get_circle_radius(1)/v.get_circle_radius(0), v.get_circle_radius(2)/v.get_circle_radius(0)))
    0.24 1.41 2.00
    >>> c = venn3_circles(subsets=[set([1,2]), set([2,3,4,5]), set([4,5,6,7,8,9,10,11])])
    '''
    # Prepare parameters
    if isinstance(subsets, dict):
        subsets = [subsets.get(t, 0) for t in ['100', '010', '110', '001', '101', '011', '111']]
    elif len(subsets) == 3:
        subsets = compute_venn3_subsets(*subsets)

    areas = compute_venn3_areas(subsets, normalize_to)
    centers, radii = solve_venn3_circles(areas)
    regions = compute_venn3_regions(centers, radii)
    colors = compute_venn3_colors(set_colors)

    if ax is None:
        ax = gca()
    prepare_venn_axes(ax, centers, radii)
    
    # Create and add patches and text
    patches = [make_venn3_region_patch(r) for r in regions]
    for (p, c) in zip(patches, colors):
        if p is not None:
            p.set_facecolor(c)
            p.set_edgecolor('none')
            p.set_alpha(alpha)
            ax.add_patch(p)
    subset_labels = [ax.text(r[2][0], r[2][1], str(s), va='center', ha='center') if r is not None else None for (r, s) in zip(regions, subsets)]

    # Position labels
    if set_labels is not None:
        # There are two situations, when set C is not on the same line with sets A and B, and when the three are on the same line.
        if abs(centers[2][1] - centers[0][1]) > tol:
            # Three circles NOT on the same line
            label_positions = [centers[0] + np.array([-radii[0] / 2, radii[0]]),
                               centers[1] + np.array([radii[1] / 2, radii[1]]),
                               centers[2] + np.array([0.0, -radii[2] * 1.1])]
            labels = [ax.text(pos[0], pos[1], txt, size='large') for (pos, txt) in zip(label_positions, set_labels)]
            labels[0].set_horizontalalignment('right')
            labels[1].set_horizontalalignment('left')
            labels[2].set_verticalalignment('top')
            labels[2].set_horizontalalignment('center')
        else:
            padding = np.mean([r * 0.1 for r in radii])
            # Three circles on the same line
            label_positions = [centers[0] + np.array([0.0, - radii[0] - padding]),
                               centers[1] + np.array([0.0, - radii[1] - padding]),
                               centers[2] + np.array([0.0, - radii[2] - padding])]
            labels = [ax.text(pos[0], pos[1], txt, size='large', ha='center', va='top') for (pos, txt) in zip(label_positions, set_labels)]
    else:
        labels = None
    return VennDiagram(patches, subset_labels, labels, centers, radii)
