// --------------------------------------------------------------------
// File: intdef.h
// Original Authors: Dominic Eales and Michael Imelfort
// --------------------------------------------------------------------
//
// OVERVIEW:
// Wrapper for defining different size ints
//
// --------------------------------------------------------------------
// Copyright (C) 2009 - 2014 Michael Imelfort and Dominic Eales
// --------------------------------------------------------------------
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation, either version 2.1 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.
//
// --------------------------------------------------------------------

#ifndef intDef_h
    #define intDef_h
    
    #include <stdint.h>
    
    //
    // how to define 32/64 bit integers on your compiler?
    // set this up so that: sizeof(uint_64t) == 8
    // and: sizeof(uint_32t) == 4
    //
    #ifndef SIZE_OF_INT
        //VHA_SIZE_OF_INT
    #endif

    //
    // All internal memory pointers are set as either 32 or 64 bit ints
    // and then wrapped up accordingly.
    //

    #ifndef SIZE_OF_IDTYPE
        //VHA_SIZE_OF_IDTYPE
    #endif

	//
	// Shorthand wrapper for our longest ints
	//
	
	#ifdef SIZE_OF_INT
	# if (SIZE_OF_INT == 64)
		typedef uint64_t uMDInt;
		typedef int64_t sMDInt;
	# elif (SIZE_OF_INT == 32)
		typedef uint32_t uMDInt;
		typedef int32_t sMDInt;
	# else
	#  error SIZE_OF_INT not correct
	# endif
		
	//
	// Id types
    //
		
	# if (SIZE_OF_IDTYPE == 64)
	   typedef uint64_t           idInt;
	# elif (SIZE_OF_IDTYPE == 32)
	   typedef uint32_t           idInt;
	# else
	#  error SIZE_OF_IDTYPE not correct
	# endif
	
	#else
	# error SIZE_OF_INT not defined
	#endif

#endif // intDef_h

