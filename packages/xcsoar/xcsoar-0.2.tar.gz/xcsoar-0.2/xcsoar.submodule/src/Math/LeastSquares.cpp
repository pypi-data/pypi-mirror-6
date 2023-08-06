/*
Copyright_License {

  XCSoar Glide Computer - http://www.xcsoar.org/
  Copyright (C) 2000-2013 The XCSoar Project
  A detailed list of copyright holders can be found in the file "AUTHORS".

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
}
*/

// leastsqs.c -- Implements a simple linear least squares best fit routine
//
// Written by Curtis Olson, started September 1997.
//
// Copyright (C) 1997  Curtis L. Olson  - http://www.flightgear.org/~curt
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Library General Public
// License as published by the Free Software Foundation; either
// version 2 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Library General Public License for more details.
//
// You should have received a copy of the GNU Library General Public
// License along with this library; if not, write to the
// Free Software Foundation, Inc., 59 Temple Place - Suite 330,
// Boston, MA  02111-1307, USA.


#include "Math/LeastSquares.hpp"

#include <math.h>

/*
Least squares fit:

  y = b0 + b1x

        n * sum(xi * yi) - (sum(xi) * sum(yi))
  b1 = ----------------------------------------
             n * sum(xi^2) - sum(xi)^2


  b0 = sum(yi) / n - b1 * (sum(xi) / n)

*/

/*
return the least squares error:

   (y[i] - y_hat[i])^2
  ---------------------
          n
*/

/*
return the maximum least squares error:

  (y[i] - y_hat[i])^2

*/

/**
 * Constructor of the LeastSquares class
 */
LeastSquares::LeastSquares() {
  Reset();
}

/**
 * Reset the LeastSquares calculator
 */
void
LeastSquares::Reset()
{
  sum_n = 0;
  sum_xi = fixed(0);
  sum_yi = fixed(0);
  sum_xi_2 = fixed(0);
  sum_xi_yi = fixed(0);
  max_error = fixed(0);
  sum_error = fixed(0);
  rms_error = fixed(0);
  sum_weights = fixed(0);
  y_max = fixed(0);
  y_min = fixed(0);
  x_min = fixed(0);
  x_max = fixed(0);
  y_ave = fixed(0);
}

/**
 * Calculate the least squares average
 */
void
LeastSquares::LeastSquaresUpdate()
{
  fixed denom = (sum_weights * sum_xi_2 - sum_xi * sum_xi);

  if (positive(fabs(denom))) {
    m = (sum_weights * sum_xi_yi - sum_xi * sum_yi) / denom;
  } else {
    m = fixed(0);
  }
  b = (sum_yi - m * sum_xi) / sum_weights;

  y_ave = m * (x_max + x_min) / 2 + b;
}

/**
 * Add a new data point to the values and calculate least squares average
 * (assumes x = sum_n + 1)
 * @param y y-Value of the new data point
 */
void
LeastSquares::LeastSquaresUpdate(fixed y)
{
  LeastSquaresUpdate(fixed(sum_n + 1), y);
}

/**
 * Add a new data point to the values and calculate least squares average
 * @param x x-Value of the new data point
 * @param y y-Value of the new data point
 * @param weight Weight of the new data point (optional)
 */
void
LeastSquares::LeastSquaresUpdate(fixed x, fixed y, fixed weight)
{
  // Add new point
  LeastSquaresAdd(x, y, weight);
  // Update calculation
  LeastSquaresUpdate();

  // Calculate error
  fixed error = fabs(y - (m * x + b));
  sum_error += sqr(error) * weight;
  if (error > max_error)
    max_error = error;
}

/**
 * Calculates the LeastSquaresError
 */
void
LeastSquares::LeastSquaresErrorUpdate()
{
  rms_error = sqrt(sum_error / sum_weights);
}

/**
 * Add a new data point to the values
 * @param x x-Value of the new data point
 * @param y y-Value of the new data point
 * @param weight Weight of the new data point (optional)
 */
void
LeastSquares::LeastSquaresAdd(fixed x, fixed y, fixed weight)
{
  // Update maximum/minimum values
  if (IsEmpty() || y > y_max)
    y_max = y;

  if (IsEmpty() || y < y_min)
    y_min = y;

  if (IsEmpty() || x > x_max)
    x_max = x;

  if (IsEmpty() || x < x_min)
    x_min = x;

  // Add point
  // TODO code: really should have a circular buffer here
  if (!slots.full())
    slots.append() = Slot(x, y, weight);

  ++sum_n;

  // Add weighted point
  sum_weights += weight;

  fixed xw = x * weight;
  fixed yw = y * weight;

  sum_xi += xw;
  sum_yi += yw;
  sum_xi_2 += sqr(xw);
  sum_xi_yi += xw * yw;
}
