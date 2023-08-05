/*-----------------------------------------------------------------------------
| Copyright (c) 2013, Nucleic Development Team.
|
| Distributed under the terms of the Modified BSD License.
|
| The full license is in the file COPYING.txt, distributed with this software.
|----------------------------------------------------------------------------*/
#pragma once

#if defined(_MSC_VER) && _MSC_VER < 1600
    typedef signed __int8 int8_t;
    typedef signed __int16 int16_t;
    typedef signed __int32 int32_t;
    typedef signed __int64 int64_t;
    typedef unsigned __int8 uint8_t;
    typedef unsigned __int16 uint16_t;
    typedef unsigned __int32 uint32_t;
    typedef unsigned __int64 uint64_t;
#else
    #include <stdint.h>
#endif
