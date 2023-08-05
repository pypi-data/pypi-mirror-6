/*
  alignlib - a library for aligning protein sequences

  $Id$

  Copyright (C) 2004 Andreas Heger

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
 */


#if HAVE_CONFIG_H
#include <config.h>
#endif

#ifndef HELPERS_TOOLKIT_H
#define HELPERS_TOOLKIT_H 1

#include "alignlib_fwd.h"
#include "alignlib_default.h"
#include "alignlib_types.h"

namespace alignlib
{

/**
 *
 * @defgroup FactoryToolkit Factory functions for @ref Toolkit objects.
 * @{
 */

/** return a new toolkit
 *
 * @param type Type of toolkit.
 * @return a @ref Toolkit object.
 */
HToolkit makeToolkit( const ToolkitType & type = ProteinAlignment );

/** @} */

/** @addtogroup Defaults
 * @{
 */

DEFINE_DEFAULT( HToolkit, getDefaultToolkit, setDefaultToolkit );

/** @} */
}

#endif	/* HELPERS_TRANSLATOR_H */
