# -*- coding: utf-8 -*-
# Horton is a development platform for electronic structure methods.
# Copyright (C) 2011-2013 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of Horton.
#
# Horton is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Horton is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
#--
#pylint: skip-file


import numpy as np
from horton import *


def get_fake_system():
    coordinates = np.array([[0.0, 1.5, 2.3], [-0.1, 1.1, 0.0], [2.0, 1.0, 0.0], [-1.0, 1.0, 1.1]])
    numbers = np.array([1, 1, 2, 2])
    sys = System(coordinates, numbers)
    origin = np.array([1.0, 0.0, 1.0])
    grid_rvecs = np.array([[0.15, 0.0, 0.0], [0.0, 0.20, 0.01], [0.01, 0.01, 0.15]])
    shape = np.array([10, 10, 20])
    pbc = np.array([1, 0, 1])
    ugrid = UniformGrid(origin, grid_rvecs, shape, pbc)
    return sys, ugrid


def test_mask_dens1():
    sys, ugrid = get_fake_system()
    rho = 10**np.random.uniform(-3, 3, ugrid.shape)
    weights = setup_weights(sys, ugrid, dens=(rho, 1e-1, 1.0))
    mask1 = rho<1e-2
    assert (weights[mask1] == 1.0).all()
    mask2 = rho>1e0
    assert (weights[mask2] == 0.0).all()
    mask3 = ~ (mask1 | mask2)
    assert (weights[mask3] < 1.0).all()
    assert (weights[mask3] > 0.0).all()


def test_mask_dens2():
    sys, ugrid = get_fake_system()
    rho = np.zeros(ugrid.shape)
    scan = np.arange(-2.0, -0.0001, 0.1)
    rho[0,0,:] = 10**scan
    weights = setup_weights(sys, ugrid, dens=(rho, 1e-1, 1.0))
    scan += 1
    assert abs(weights[0,0,:] - (0.25*scan*(scan*scan-3)+0.5)).max() < 1e-10


def test_mask_near1():
    sys, ugrid = get_fake_system()
    weights = setup_weights(sys, ugrid, near={1: (0.5, 0.5), 2: (1.0, 0.2)})
    assert (weights >= 0.0).all()
    assert (weights <= 1.0).all()
    # find the point close to atom 2 and check that the weight is zero
    grid_cell = ugrid.get_grid_cell()
    i = np.round(grid_cell.to_frac(sys.coordinates[2] - ugrid.origin)).astype(int)
    i[0] = i[0]%10
    i[2] = i[2]%20
    assert weights[i[0], i[1], i[2]] == 0.0


def test_mask_near2():
    sys, ugrid = get_fake_system()
    weights = setup_weights(sys, ugrid, near={1: (0.5, 0.5), 2: (1.0, 0.2)})
    weights1 = setup_weights(sys, ugrid, near={1: (0.5, 0.5)})
    weights2 = setup_weights(sys, ugrid, near={2: (1.0, 0.2)})
    assert abs(weights - weights1*weights2).max() < 1e-10


def test_mask_near3():
    sys, ugrid = get_fake_system()
    weights = setup_weights(sys, ugrid, near={0: (0.5, 0.5)})
    weights1 = setup_weights(sys, ugrid, near={1: (0.5, 0.5)})
    weights2 = setup_weights(sys, ugrid, near={2: (0.5, 0.5)})
    assert abs(weights - weights1*weights2).max() < 1e-10


def test_mask_far():
    sys, ugrid = get_fake_system()
    weights = setup_weights(sys, ugrid, far=(1.0, 0.5))
    assert (weights >= 0.0).all()
    assert (weights <= 1.0).all()
    # find the point close to atom 2 and check that the weight is one
    grid_cell = ugrid.get_grid_cell()
    i = np.round(grid_cell.to_frac(sys.coordinates[2] - ugrid.origin)).astype(int)
    i[0] = i[0]%10
    i[2] = i[2]%20
    assert weights[i[0], i[1], i[2]] == 1.0
