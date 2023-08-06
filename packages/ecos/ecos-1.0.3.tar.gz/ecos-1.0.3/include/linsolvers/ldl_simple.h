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
 * Defines the struct needed for computing the simple LDL.
 */

#ifndef __LDL_SIMPLE_H__
#define __LDL_SIMPLE_H__

#include "../spla.h"

typedef struct ldl_simple {
    spmat*  L;       /* LDL factor L                              */
    pfloat* D;       /* diagonal matrix D                         */

    idxint* Parent;  /* Elimination tree of factorization         */
    idxint* Sign;    /* Permuted sign vector for regularization   */
    idxint* Pattern; /* idxint workspace needed for factorization */
    idxint* Flag;    /* idxint workspace needed for factorization */
    idxint* Lnz;     /* idxint workspace needed for factorization */
};



#endif // __LDL_SIMPLE_H__
