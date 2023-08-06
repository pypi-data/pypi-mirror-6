/*
 * ECOS - Embedded Conic Solver.
 * Copyright (C) 2012-14 Alexander Domahidi [domahidi@control.ee.ethz.ch],
 * Automatic Control Laboratory, ETH Zurich.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


/**
 * The linear solver module.
 * Handles all memory related to the solution of linear systems:
 * - permutations
 * - symbolic factorization
 * - numeric factorization
 */


#ifndef __LINSOLVER_H__
#define __LINSOLVER_H__

#include "spla.h"
#include "kkt.h"

 #include "linsolvers/ldl_simple.h"

/* enum for linsolver types. */
typedef enum {LDL_SIMPLE, NOT_YET_IMPLEMENTED} solver_t;

/* Struct for linear system solver. */
typedef struct linsolver {
    solver_t type;
    union solver {
        ldl_simple ldl;
        /* other linear solver types go here */
    } solver;
} linsolver;

/* Return codes */
#define LINSOLVER_PROBLEM (0)
#define LINSOLVER_OK      (1)

/* Creates a linear system solver with the given type */
/**
 * eps      is the threshold for dynamic regularization.
 * delta    is the amount of dynamic regularization to apply.
 */
linsolver *create_linsolver(solver_t type, const pfloat eps, const pfloat delta);

/* Compute the sparse matrix ordering. Modifies the KKT struct. */
idxint order(linsolver *solver, kkt *KKT);

/* Compute the symbolic ordering. Modifies the KKT struct. */
idxint symbolic_factor(linsolver *solver, kkt *KKT);

/* Compute the numeric factorization. Modifies the KKT struct. */
idxint factor(linsolver *solver, kkt *KKT);

/* Solve for KKT * x = b */
idxint solve(linsolver *solver, kkt *KKT, pfloat *x, pfloat *b);

/* Frees any memory associated with a linear system solver. */
linsolver *free_linsolver(linsolver *solver);



#endif
