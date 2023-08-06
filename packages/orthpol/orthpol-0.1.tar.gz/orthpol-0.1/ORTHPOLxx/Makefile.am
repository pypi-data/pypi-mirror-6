AUTOMAKE_OPTION = cygnus

AUTOMAKE_OPTIONS = subdir-objects

lib_LTLIBRARIES = liborthpol-1.0.la

liborthpol_1_0_la_SOURCES = src/cheb.f src/chri.f src/d1mach.f src/dcheb.f src/dchri.f src/dgauss.f src/dgchri.f src/dkern.f src/dknum.f src/dlancz.f src/dlob.f src/dmcdis.f src/dmcheb.f src/dqgp.f src/dradau.f src/drecur.f src/dsti.f src/gauss.f src/gchri.f src/i1mach.f src/kern.f src/knum.f src/lancz.f src/lob.f src/mccheb.f src/mcdis.f src/nu0her.f src/nu0jac.f src/nu0lag.f src/qgp.f src/r1mach.f src/radau.f src/recur.f src/sti.f src/ORTHPOLPP.cpp

library_includedir = $(includedir)/liborthpol-1.0/ORTHPOLxx
library_include_HEADERS = src/fortran.h src/f77char.h src/f77cmplx.h src/f77matrix.h src/ORTHPOLPP.hpp

liborthpol_libincludedir = $(libdir)/liborthpol-1.0/include
nodist_liborthpol_libinclude_HEADERS = config.h

LIBRARY_VERSION = 1:0:0
liborthpol_1_0_la_LDFLAGS = -version-info $(LIBRARY_VERSION) -lgfortran

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = liborthpol-1.0.pc

#ACLOCAL_AMFLAGS = -I m4