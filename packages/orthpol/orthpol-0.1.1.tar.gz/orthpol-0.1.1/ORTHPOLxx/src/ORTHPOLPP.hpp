#ifndef PORTINGSTUB_HPP
#define PORTINGSTUB_HPP

#define F77_STUB_REQUIRED
#include "fortran.h"

REAL_FUNCTION_F77 r1mach_(int& I);
REAL_FUNCTION r1mach(INTEGER& I);

DOUBLE_PRECISION_FUNCTION_F77 d1mach_(int& I);
DOUBLE_PRECISION_FUNCTION d1mach(INTEGER& I);

SUBROUTINE_F77 cheb_(int& n, 
		     float* a, 
		     float* b, 
		     float* fnu, 
		     float* alpha, 
		     float* beta, 
		     float* s, 
		     int& ierr,
		     float* s0,
		     float* s1,
		     float* s2);
SUBROUTINE cheb(INTEGER& n,
		REAL* a,
		REAL* b,
		REAL* fnu,
		REAL* alpha,
		REAL* beta,
		REAL* s,
		INTEGER& ierr,
		REAL* s0,
		REAL* s1,
		REAL* s2);

SUBROUTINE_F77 dcheb_(int& n, 
		      double* a, 
		      double* b, 
		      double* fnu, 
		      double* alpha, 
		      double* beta, 
		      double* s, 
		      int& ierr,
		      double* s0,
		      double* s1,
		      double* s2);
SUBROUTINE dcheb(INTEGER& n,
		 DOUBLE_PRECISION* a,
		 DOUBLE_PRECISION* b,
		 DOUBLE_PRECISION* fnu,
		 DOUBLE_PRECISION* alpha,
		 DOUBLE_PRECISION* beta,
		 DOUBLE_PRECISION* s,
		 INTEGER& ierr,
		 DOUBLE_PRECISION* s0,
		 DOUBLE_PRECISION* s1,
		 DOUBLE_PRECISION* s2);

SUBROUTINE_F77 chri_(int& n,
		    int& iopt,
		    float* a,
		    float* b,
		    float& x,
		    float& y,
		    float& hr,
		    float& hi,
		    float* alpha,
		    float* beta,
		    int& ierr);
SUBROUTINE chri(INTEGER& n,
		INTEGER& iopt,
		REAL* a,
		REAL* b,
		REAL& x,
		REAL& y,
		REAL& hr,
		REAL& hi,
		REAL* alpha,
		REAL* beta,
		INTEGER& ierr);

SUBROUTINE_F77 dchri_(int& n,
		      int& iopt,
		      double* a,
		      double* b,
		      double& x,
		      double& y,
		      double& hr,
		      double& hi,
		      double* alpha,
		      double* beta,
		      int& ierr);
SUBROUTINE dchri(INTEGER& n,
		 INTEGER& iopt,
		 DOUBLE_PRECISION* a,
		 DOUBLE_PRECISION* b,
		 DOUBLE_PRECISION& x,
		 DOUBLE_PRECISION& y,
		 DOUBLE_PRECISION& hr,
		 DOUBLE_PRECISION& hi,
		 DOUBLE_PRECISION* alpha,
		 DOUBLE_PRECISION* beta,
		 INTEGER& ierr);

SUBROUTINE_F77 gauss_(int& n,
		      float* alpha,
		      float* beta,
		      float& eps,
		      float* zero,
		      float* weight,
		      int& ierr,
		      float* e);
SUBROUTINE gauss(INTEGER& n,
		 REAL* alpha,
		 REAL* beta,
		 REAL& eps,
		 REAL* zero,
		 REAL* weight,
		 INTEGER& ierr,
		 REAL* e);

SUBROUTINE_F77 dgauss_(int& n,
		       double* alpha,
		       double* beta,
		       double& eps,
		       double* zero,
		       double* weight,
		       int& ierr,
		       double* e);
SUBROUTINE dgauss(INTEGER& n,
		  DOUBLE_PRECISION* alpha,
		  DOUBLE_PRECISION* beta,
		  DOUBLE_PRECISION& eps,
		  DOUBLE_PRECISION* zero,
		  DOUBLE_PRECISION* weight,
		  INTEGER& ierr,
		  DOUBLE_PRECISION* e);

SUBROUTINE_F77 gchri_(int& n,
		      int& iopt,
		      int& nu0,
		      int& numax,
		      float& eps,
		      float* a,
		      float* b,
		      float& x,
		      float& y,
		      float* alpha,
		      float* beta,
		      int& nu,
		      int& ierr,
		      int& ierrc, // inherited error flag from cheb
		      float* fnu, // dim 2*n
		      float* s,   // dim n
		      float* s0,  // dim 2*n
		      float* s1,  // dim 2*n
		      float* s2 // dim 2*n
		      );
SUBROUTINE gchri(INTEGER& n,
		 INTEGER& iopt,
		 INTEGER& nu0,
		 INTEGER& numax,
		 REAL& eps,
		 REAL* a,
		 REAL* b,
		 REAL& x,
		 REAL& y,
		 REAL* alpha,
		 REAL* beta,
		 INTEGER& nu,
		 INTEGER& ierr,
		 INTEGER& ierrc,
		 REAL* fnu,
		 REAL* s,
		 REAL* s0,
		 REAL* s1,
		 REAL* s2);

SUBROUTINE_F77 dgchri_(int& n,
		       int& iopt,
		       int& nu0,
		       int& numax,
		       double& eps,
		       double* a,
		       double* b,
		       double& x,
		       double& y,
		       double* alpha,
		       double* beta,
		       int& nu,
		       int& ierr,
		       int& ierrc, // inherited error flag from cheb
		       double* fnu, // dim 2*n
		       double* s,   // dim n
		       double* s0,  // dim 2*n
		       double* s1,  // dim 2*n
		       double* s2 // dim 2*n
		       );
SUBROUTINE dgchri(INTEGER& n,
		  INTEGER& iopt,
		  INTEGER& nu0,
		  INTEGER& numax,
		  DOUBLE_PRECISION& eps,
		  DOUBLE_PRECISION* a,
		  DOUBLE_PRECISION* b,
		  DOUBLE_PRECISION& x,
		  DOUBLE_PRECISION& y,
		  DOUBLE_PRECISION* alpha,
		  DOUBLE_PRECISION* beta,
		  INTEGER& nu,
		  INTEGER& ierr,
		  INTEGER& ierrc,
		  DOUBLE_PRECISION* fnu,
		  DOUBLE_PRECISION* s,
		  DOUBLE_PRECISION* s0,
		  DOUBLE_PRECISION* s1,
		  DOUBLE_PRECISION* s2);

SUBROUTINE_F77 lancz_(int &n,
		      int& ncap,
		      float* x,
		      float* w,
		      float* alpha,
		      float* beta,
		      int& ierr,
		      float* p0,
		      float* p1);
SUBROUTINE lancz(INTEGER& n,
		 INTEGER& ncap,
		 REAL* x,
		 REAL* w,
		 REAL* alpha,
		 REAL* beta,
		 INTEGER& ierr,
		 REAL* p0,
		 REAL* p1);

SUBROUTINE_F77 dlancz_(int &n,
		       int& ncap,
		       double* x,
		       double* w,
		       double* alpha,
		       double* beta,
		       int& ierr,
		       double* p0,
		       double* p1);
SUBROUTINE dlancz(INTEGER& n,
		  INTEGER& ncap,
		  DOUBLE_PRECISION* x,
		  DOUBLE_PRECISION* w,
		  DOUBLE_PRECISION* alpha,
		  DOUBLE_PRECISION* beta,
		  INTEGER& ierr,
		  DOUBLE_PRECISION* p0,
		  DOUBLE_PRECISION* p1);

SUBROUTINE_F77 lob_(int& n,
		    float* alpha,
		    float* beta,
		    float& aleft,
		    float& right,
		    float* zero,
		    float* weight,
		    int& ierr,
		    float* e,  // dim n+2
		    float* a,  // dim n+2
		    float* b   // dim n+2
		    );
SUBROUTINE lob(INTEGER& n,
	       REAL* alpha,
	       REAL* beta,
	       REAL& aleft,
	       REAL& right,
	       REAL* zero,
	       REAL* weight,
	       INTEGER& ierr,
	       REAL* e,
	       REAL* a,
	       REAL* b);

SUBROUTINE_F77 dlob_(int& n,
		     double* alpha,
		     double* beta,
		     double& aleft,
		     double& right,
		     double* zero,
		     double* weight,
		     int& ierr,
		     double* e,  // dim n+2
		     double* a,  // dim n+2
		     double* b   // dim n+2
		     );
SUBROUTINE dlob(INTEGER& n,
		DOUBLE_PRECISION* alpha,
		DOUBLE_PRECISION* beta,
		DOUBLE_PRECISION& aleft,
		DOUBLE_PRECISION& right,
		DOUBLE_PRECISION* zero,
		DOUBLE_PRECISION* weight,
		INTEGER& ierr,
		DOUBLE_PRECISION* e,
		DOUBLE_PRECISION* a,
		DOUBLE_PRECISION* b);

SUBROUTINE_F77 mccheb_(int& n,
		       int& ncapm,
		       int& mc,
		       int& mp,
		       float* xp, // dim mp
		       float* yp, // dim mp
		       // function quad is removed and up to the user to be implemented
		       float& eps,
		       int& iq,
		       int& idelta,
		       int& finl, // Needed by qgp (logical)
		       int& finr, // Needed by qgp (logical)
		       float* endl, // Needed by qgp
		       float* endr, // Needed by qgp
		       float* xfer, // Needed by qgp
		       float* wfer, // Needed by qgp
		       float* a,
		       float* b,
		       float* fnu,
		       float* alpha, // dim n
		       float* beta, // dim n
		       int& ncap,
		       int& kount,
		       int& ierr,
		       float* be, // dimension n
		       float* x, // dim ncapm
		       float* w, // dim ncapm
		       float* xm, // dim mc*ncapm+mp
		       float* wm, // dim mc*ncapm+mp
		       float* s, // dim mc*ncapm+mp ?
		       float* s0, // dim mc*ncapm+mp ?
		       float* s1, // dim mc*ncapm+mp ?
		       float* s2 // dim mc*ncapm+mp  ?
		       );
SUBROUTINE mcheb(INTEGER& n,
		  INTEGER& ncapm,
		  INTEGER& mc,
		  INTEGER& mp,
		  REAL* xp,
		  REAL* yp,
		  REAL& eps,
		  INTEGER& iq,
		  INTEGER& idelta,
		  LOGICAL& finl,
		  LOGICAL& finr,
		  REAL* endl,
		  REAL* endr,
		  REAL* xfer,
		  REAL* wfer,
		  REAL* a,
		  REAL* b,
		  REAL* fnu,
		  REAL* alpha,
		  REAL* beta,
		  INTEGER& ncap,
		  INTEGER& kount,
		  INTEGER& ierr,
		  REAL* be,
		  REAL* x,
		  REAL* w,
		  REAL* xm,
		  REAL* wm,
		  REAL* s,
		  REAL* s0,
		  REAL* s1,
		  REAL* s2);

SUBROUTINE_F77 dmcheb_(int& n,
			int& ncapm,
			int& mc,
			int& mp,
			double* xp, // dim mp
			double* yp, // dim mp
			// function quad is removed and up to the user to be implemented
			double& eps,
			int& iq,
			int& idelta,
			int& finl, // Needed by qgp (logical)
			int& finr, // Needed by qgp (logical)
			double* endl, // Needed by qgp
			double* endr, // Needed by qgp
			double* xfer, // Needed by qgp
			double* wfer, // Needed by qgp
			double* a, // dim 2*n-1
			double* b, // dim 2*n-1
			double* fnu,
			double* alpha, // dim n
			double* beta, // dim n
			int& ncap,
			int& kount,
			int& ierr,
			double* be, // dimension n
			double* x, // dim ncapm
			double* w, // dim ncapm
			double* xm, // dim mc*ncapm+mp
			double* wm, // dim mc*ncapm+mp
			double* s, // dim mc*ncapm+mp ?
			double* s0, // dim mc*ncapm+mp ?
			double* s1, // dim mc*ncapm+mp ?
			double* s2 // dim mc*ncapm+mp  ?
			);
SUBROUTINE dmcheb(INTEGER& n,
		   INTEGER& ncapm,
		   INTEGER& mc,
		   INTEGER& mp,
		   DOUBLE_PRECISION* xp,
		   DOUBLE_PRECISION* yp,
		   DOUBLE_PRECISION& eps,
		   INTEGER& iq,
		   INTEGER& idelta,
		   LOGICAL& finl,
		   LOGICAL& finr,
		   DOUBLE_PRECISION* endl,
		   DOUBLE_PRECISION* endr,
		   DOUBLE_PRECISION* xfer,
		   DOUBLE_PRECISION* wfer,
		   DOUBLE_PRECISION* a,
		   DOUBLE_PRECISION* b,
		   DOUBLE_PRECISION* fnu,
		   DOUBLE_PRECISION* alpha,
		   DOUBLE_PRECISION* beta,
		   INTEGER& ncap,
		   INTEGER& kount,
		   INTEGER& ierr,
		   DOUBLE_PRECISION* be,
		   DOUBLE_PRECISION* x,
		   DOUBLE_PRECISION* w,
		   DOUBLE_PRECISION* xm,
		   DOUBLE_PRECISION* wm,
		   DOUBLE_PRECISION* s,
		   DOUBLE_PRECISION* s0,
		   DOUBLE_PRECISION* s1,
		   DOUBLE_PRECISION* s2);

SUBROUTINE_F77 mcdis_(int& n,
		     int& ncapm,
		     int& mc,
		     int& mp,
		     float* xp, // dim mp
		     float* yp, // dim mp
		     // function quad is removed and up to the user to be implemented
		     float& eps,
		     int& iq,
		     int& idelta,
		     int& irout,
		     int& finl, // Needed by qgp (logical)
		     int& finr, // Needed by qgp (logical)
		     float* endl, // Needed by qgp
		     float* endr, // Needed by qgp
		     float* xfer, // Needed by qgp
		     float* wfer, // Needed by qgp
		     float* alpha, // dim n
		     float* beta, // dim n
		     int& ncap,
		     int& kount,
		     int& ierr,
		     int& ie,
		     float* be, // dimension n
		     float* x, // dim ncapm
		     float* w, // dim ncapm
		     float* xm, // dim mc*ncapm+mp
		     float* wm, // dim mc*ncapm+mp
		     float* p0, // dim mc*ncapm+mp
		     float* p1, // dim mc*ncapm+mp
		     float* p2 // dim mc*ncapm+mp
		     );
SUBROUTINE mcdis(INTEGER& n,
		 INTEGER& ncapm,
		 INTEGER& mc,
		 INTEGER& mp,
		 REAL* xp,
		 REAL* yp,
		 REAL& eps,
		 INTEGER& iq,
		 INTEGER& idelta,
		 INTEGER& irout,
		 LOGICAL& finl,
		 LOGICAL& finr,
		 REAL* endl,
		 REAL* endr,
		 REAL* xfer,
		 REAL* wfer,
		 REAL* alpha,
		 REAL* beta,
		 INTEGER& ncap,
		 INTEGER& kount,
		 INTEGER& ierr,
		 INTEGER& ie,
		 REAL* be,
		 REAL* x,
		 REAL* w,
		 REAL* xm,
		 REAL* wm,
		 REAL* p0,
		 REAL* p1,
		 REAL* p2);

SUBROUTINE_F77 dmcdis_(int& n,
		       int& ncapm,
		       int& mc,
		       int& mp,
		       double* xp, // dim mp
		       double* yp, // dim mp
		       // function quad is removed and up to the user to be implemented
		       double& eps,
		       int& iq,
		       int& idelta,
		       int& irout,
		       int& finl, // Needed by qgp (logical)
		       int& finr, // Needed by qgp (logical)
		       double* endl, // Needed by qgp
		       double* endr, // Needed by qgp
		       double* xfer, // Needed by qgp
		       double* wfer, // Needed by qgp
		       double* alpha, // dim n
		       double* beta, // dim n
		       int& ncap,
		       int& kount,
		       int& ierr,
		       int& ie,
		       double* be, // dimension n
		       double* x, // dim ncapm
		       double* w, // dim ncapm
		       double* xm, // dim mc*ncapm+mp
		       double* wm, // dim mc*ncapm+mp
		       double* p0, // dim mc*ncapm+mp
		       double* p1, // dim mc*ncapm+mp
		       double* p2 // dim mc*ncapm+mp
		       );
SUBROUTINE dmcdis(INTEGER& n,
		  INTEGER& ncapm,
		  INTEGER& mc,
		  INTEGER& mp,
		  DOUBLE_PRECISION* xp,
		  DOUBLE_PRECISION* yp,
		  DOUBLE_PRECISION& eps,
		  INTEGER& iq,
		  INTEGER& idelta,
		  INTEGER& irout,
		  LOGICAL& finl,
		  LOGICAL& finr,
		  DOUBLE_PRECISION* endl,
		  DOUBLE_PRECISION* endr,
		  DOUBLE_PRECISION* xfer,
		  DOUBLE_PRECISION* wfer,
		  DOUBLE_PRECISION* alpha,
		  DOUBLE_PRECISION* beta,
		  INTEGER& ncap,
		  INTEGER& kount,
		  INTEGER& ierr,
		  INTEGER& ie,
		  DOUBLE_PRECISION* be,
		  DOUBLE_PRECISION* x,
		  DOUBLE_PRECISION* w,
		  DOUBLE_PRECISION* xm,
		  DOUBLE_PRECISION* wm,
		  DOUBLE_PRECISION* p0,
		  DOUBLE_PRECISION* p1,
		  DOUBLE_PRECISION* p2);

SUBROUTINE_F77 nu0her_(int& n,
		       COMPLEX<double>& z,
		       double& eps);
SUBROUTINE nu0her(INTEGER& n,
		  COMPLEX<DOUBLE_PRECISION>& z,
		  DOUBLE_PRECISION& eps);

SUBROUTINE_F77 nu0jac_(int& n,
		       COMPLEX<double>& z,
		       double& eps);
SUBROUTINE nu0jac(INTEGER& n,
		  COMPLEX<DOUBLE_PRECISION>& z,
		  DOUBLE_PRECISION& eps);

SUBROUTINE_F77 nu0lag_(int& n,
		       COMPLEX<double>& z,
		       double& eps);
SUBROUTINE nu0lag(INTEGER& n,
		  COMPLEX<DOUBLE_PRECISION>& z,
		  DOUBLE_PRECISION& eps);

SUBROUTINE_F77 qgp_(int& n,
		    float* x,
		    float* w,
		    int& i,
		    int& ierr,
		    int& mc,
		    int& finl,
		    int& finr,
		    float* endl,
		    float* endr,
		    float* xfer,
		    float* wfer
		    // Function wf(x,i) removed for porting. Up to the user to implement it.
		    );
SUBROUTINE qgp(INTEGER& n,
	       REAL* x,
	       REAL* w,
	       INTEGER& i,
	       INTEGER& ierr,
	       INTEGER& mc,
	       LOGICAL& finl,
	       LOGICAL& finr,
	       REAL* endl,
	       REAL* endr,
	       REAL* xfer,
	       REAL* wfer);

SUBROUTINE_F77 dqgp_(int& n,
		     double* x,
		     double* w,
		     int& i,
		     int& ierr,
		     int& mc,
		     int& finl,
		     int& finr,
		     double* endl,
		     double* endr,
		     double* xfer,
		     double* wfer
		     // Function wf(x,i) removed for porting. Up to the user to implement it.
		     );
SUBROUTINE dqgp(INTEGER& n,
		DOUBLE_PRECISION* x,
		DOUBLE_PRECISION* w,
		INTEGER& i,
		INTEGER& ierr,
		INTEGER& mc,
		LOGICAL& finl,
		LOGICAL& finr,
		DOUBLE_PRECISION* endl,
		DOUBLE_PRECISION* endr,
		DOUBLE_PRECISION* xfer,
		DOUBLE_PRECISION* wfer);

SUBROUTINE_F77 radau_(int& n,
		      float* alpha,
		      float* beta,
		      float& end,
		      float* zero,
		      float* weight,
		      int& ierr,
		      float* e, // dim n+2
		      float* a, // dim n+2
		      float* b // dim n+2
		      );
SUBROUTINE radau(INTEGER& n,
		 REAL* alpha,
		 REAL* beta,
		 REAL& end,
		 REAL* zero,
		 REAL* weight,
		 INTEGER& ierr,
		 REAL* e,
		 REAL* a,
		 REAL* b);

SUBROUTINE_F77 dradau_(int& n,
		       double* alpha,
		       double* beta,
		       double& end,
		       double* zero,
		       double* weight,
		       int& ierr,
		       double* e, // dim n+2
		       double* a, // dim n+2
		       double* b // dim n+2
		       );
SUBROUTINE dradau(INTEGER& n,
		  DOUBLE_PRECISION* alpha,
		  DOUBLE_PRECISION* beta,
		  DOUBLE_PRECISION& end,
		  DOUBLE_PRECISION* zero,
		  DOUBLE_PRECISION* weight,
		  INTEGER& ierr,
		  DOUBLE_PRECISION* e,
		  DOUBLE_PRECISION* a,
		  DOUBLE_PRECISION* b);

SUBROUTINE_F77 recur_(int& n,
		      int& ipoly, 
		      float& al,
		      float& be,
		      float* a, 
		      float* b, 
		      int& ierr);
SUBROUTINE recur(INTEGER& n,
		 INTEGER& ipoly,
		 REAL& al,
		 REAL& be,
		 REAL* a,
		 REAL* b,
		 INTEGER& ierr);

SUBROUTINE_F77 drecur_(int& n, 
		       int& ipoly, 
		       double& al, 
		       double& be, 
		       double* a, 
		       double* b, 
		       int& ierr);
SUBROUTINE drecur(INTEGER& n,
		  INTEGER& ipoly,
		  DOUBLE_PRECISION& al,
		  DOUBLE_PRECISION& be,
		  DOUBLE_PRECISION* a,
		  DOUBLE_PRECISION* b,
		  INTEGER& ierr);

SUBROUTINE_F77 sti_(int& n,
		    int& ncap,
		    float* x,
		    float* w,
		    float* alpha,
		    float* beta,
		    int& ierr,
		    float* p0,
		    float* p1,
		    float* p2);
SUBROUTINE sti(INTEGER& n,
	       INTEGER& ncap,
	       REAL* x,
	       REAL* w,
	       REAL* alpha,
	       REAL* beta,
	       INTEGER& ierr,
	       REAL* p0,
	       REAL* p1,
	       REAL* p2);

SUBROUTINE_F77 dsti_(int& n,
		     int& ncap,
		     double* x,
		     double* w,
		     double* alpha,
		     double* beta,
		     int& ierr,
		     double* p0,
		     double* p1,
		     double* p2);
SUBROUTINE dsti(INTEGER& n,
		INTEGER& ncap,
		DOUBLE_PRECISION* x,
		DOUBLE_PRECISION* w,
		DOUBLE_PRECISION* alpha,
		DOUBLE_PRECISION* beta,
		INTEGER& ierr,
		DOUBLE_PRECISION* p0,
		DOUBLE_PRECISION* p1,
		DOUBLE_PRECISION* p2);

namespace orthpol
{
  void set_quad_callback(void (*pointer)(int& n, float* x, float* w, int& i, int& ierr));
  void set_dquad_callback(void (*pointer)(int& n, double* x, double* w, int& i, int& ierr));
  void set_wf_callback(float (*pointer)(float& x, int& i));
  void set_dwf_callback(double (*pointer)(double& x, int& i));

  float r1mach(int& I);
  double d1mach(int& I);

  void cheb(int& n, 
	    float* a, 
	    float* b, 
	    float* fnu, 
	    float* alpha, 
	    float* beta, 
	    float* s, 
	    int& ierr,
	    float* s0,
	    float* s1,
	    float* s2);
  void dcheb(int& n, 
	     double* a, 
	     double* b, 
	     double* fnu, 
	     double* alpha, 
	     double* beta, 
	     double* s, 
	     int& ierr,
	     double* s0,
	     double* s1,
	     double* s2);

  void chri(int& n,
	    int& iopt,
	    float* a,
	    float* b,
	    float& x,
	    float& y,
	    float& hr,
	    float& hi,
	    float* alpha,
	    float* beta,
	    int& ierr);
  void dchri(int& n,
	     int& iopt,
	     double* a,
	     double* b,
	     double& x,
	     double& y,
	     double& hr,
	     double& hi,
	     double* alpha,
	     double* beta,
	     int& ierr);

  void gauss(int& n,
	     float* alpha,
	     float* beta,
	     float& eps,
	     float* zero,
	     float* weight,
	     int& ierr,
	     float* e);
  void dgauss(int& n,
	      double* alpha,
	      double* beta,
	      double& eps,
	      double* zero,
	      double* weight,
	      int& ierr,
	      double* e);

  void gchri(int& n,
	     int& iopt,
	     int& nu0,
	     int& numax,
	     float& eps,
	     float* a,
	     float* b,
	     float& x,
	     float& y,
	     float* alpha,
	     float* beta,
	     int& nu,
	     int& ierr,
	     int& ierrc, // inherited error flag from cheb
	     float* fnu, // dim 2*n
	     float* s,   // dim n
	     float* s0,  // dim 2*n
	     float* s1,  // dim 2*n
	     float* s2 // dim 2*n
	     );
  void dgchri(int& n,
	      int& iopt,
	      int& nu0,
	      int& numax,
	      double& eps,
	      double* a,
	      double* b,
	      double& x,
	      double& y,
	      double* alpha,
	      double* beta,
	      int& nu,
	      int& ierr,
	      int& ierrc, // inherited error flag from cheb
	      double* fnu, // dim 2*n
	      double* s,   // dim n
	      double* s0,  // dim 2*n
	      double* s1,  // dim 2*n
	      double* s2 // dim 2*n
	      );

  void lancz(int &n,
	     int& ncap,
	     float* x,
	     float* w,
	     float* alpha,
	     float* beta,
	     int& ierr,
	     float* p0,
	     float* p1);
  void dlancz(int &n,
	      int& ncap,
	      double* x,
	      double* w,
	      double* alpha,
	      double* beta,
	      int& ierr,
	      double* p0,
	      double* p1);

  void lob(int& n,
	   float* alpha,
	   float* beta,
	   float& aleft,
	   float& right,
	   float* zero,
	   float* weight,
	   int& ierr,
	   float* e,  // dim n+2
	   float* a,  // dim n+2
	   float* b   // dim n+2
	   );
  void dlob(int& n,
	    double* alpha,
	    double* beta,
	    double& aleft,
	    double& right,
	    double* zero,
	    double* weight,
	    int& ierr,
	    double* e,  // dim n+2
	    double* a,  // dim n+2
	    double* b   // dim n+2
	    );

  void mccheb(int& n,
	      int& ncapm,
	      int& mc,
	      int& mp,
	      float* xp, // dim mp
	      float* yp, // dim mp
	      // function quad is removed and up to the user to be implemented
	      float& eps,
	      int& iq,
	      int& idelta,
	      int& finl, // Needed by qgp (logical)
	      int& finr, // Needed by qgp (logical)
	      float* endl, // Needed by qgp
	      float* endr, // Needed by qgp
	      float* xfer, // Needed by qgp
	      float* wfer, // Needed by qgp
	      float* a,
	      float* b,
	      float* fnu,
	      float* alpha, // dim n
	      float* beta, // dim n
	      int& ncap,
	      int& kount,
	      int& ierr,
	      float* be, // dimension n
	      float* x, // dim ncapm
	      float* w, // dim ncapm
	      float* xm, // dim mc*ncapm+mp
	      float* wm, // dim mc*ncapm+mp
	      float* s, // dim mc*ncapm+mp ?
	      float* s0, // dim mc*ncapm+mp ?
	      float* s1, // dim mc*ncapm+mp ?
	      float* s2 // dim mc*ncapm+mp  ?
	      );
  void dmcheb(int& n,
	      int& ncapm,
	      int& mc,
	      int& mp,
	      double* xp, // dim mp
	      double* yp, // dim mp
	      // function quad is removed and up to the user to be implemented
	      double& eps,
	      int& iq,
	      int& idelta,
	      int& finl, // Needed by qgp (logical)
	      int& finr, // Needed by qgp (logical)
	      double* endl, // Needed by qgp
	      double* endr, // Needed by qgp
	      double* xfer, // Needed by qgp
	      double* wfer, // Needed by qgp
	      double* a, // dim 2*n-1
	      double* b, // dim 2*n-1
	      double* fnu,
	      double* alpha, // dim n
	      double* beta, // dim n
	      int& ncap,
	      int& kount,
	      int& ierr,
	      double* be, // dimension n
	      double* x, // dim ncapm
	      double* w, // dim ncapm
	      double* xm, // dim mc*ncapm+mp
	      double* wm, // dim mc*ncapm+mp
	      double* s, // dim mc*ncapm+mp ?
	      double* s0, // dim mc*ncapm+mp ?
	      double* s1, // dim mc*ncapm+mp ?
	      double* s2 // dim mc*ncapm+mp  ?
	      );

  void mcdis(int& n,
	     int& ncapm,
	     int& mc,
	     int& mp,
	     float* xp, // dim mp
	     float* yp, // dim mp
	     // function quad is removed and up to the user to be implemented
	     float& eps,
	     int& iq,
	     int& idelta,
	     int& irout,
	     int& finl, // Needed by qgp (logical)
	     int& finr, // Needed by qgp (logical)
	     float* endl, // Needed by qgp
	     float* endr, // Needed by qgp
	     float* xfer, // Needed by qgp
	     float* wfer, // Needed by qgp
	     float* alpha, // dim n
	     float* beta, // dim n
	     int& ncap,
	     int& kount,
	     int& ierr,
	     int& ie,
	     float* be, // dimension n
	     float* x, // dim ncapm
	     float* w, // dim ncapm
	     float* xm, // dim mc*ncapm+mp
	     float* wm, // dim mc*ncapm+mp
	     float* p0, // dim mc*ncapm+mp
	     float* p1, // dim mc*ncapm+mp
	     float* p2 // dim mc*ncapm+mp
	     );
  void dmcdis(int& n,
	      int& ncapm,
	      int& mc,
	      int& mp,
	      double* xp, // dim mp
	      double* yp, // dim mp
	      // function quad is removed and up to the user to be implemented
	      double& eps,
	      int& iq,
	      int& idelta,
	      int& irout,
	      int& finl, // Needed by qgp (logical)
	      int& finr, // Needed by qgp (logical)
	      double* endl, // Needed by qgp
	      double* endr, // Needed by qgp
	      double* xfer, // Needed by qgp
	      double* wfer, // Needed by qgp
	      double* alpha, // dim n
	      double* beta, // dim n
	      int& ncap,
	      int& kount,
	      int& ierr,
	      int& ie,
	      double* be, // dimension n
	      double* x, // dim ncapm
	      double* w, // dim ncapm
	      double* xm, // dim mc*ncapm+mp
	      double* wm, // dim mc*ncapm+mp
	      double* p0, // dim mc*ncapm+mp
	      double* p1, // dim mc*ncapm+mp
	      double* p2 // dim mc*ncapm+mp
	      );

  void nu0her(int& n,
	      COMPLEX<double>& z,
	      double& eps);

  void nu0jac(int& n,
	      COMPLEX<double>& z,
	      double& eps);

  void nu0lag(int& n,
	      COMPLEX<double>& z,
	      double& eps);

  void qgp(int& n,
	   float* x,
	   float* w,
	   int& i,
	   int& ierr,
	   int& mc,
	   int& finl,
	   int& finr,
	   float* endl,
	   float* endr,
	   float* xfer,
	   float* wfer
	   // Function wf(x,i) removed for porting. Up to the user to implement it.
	   );
  void dqgp(int& n,
	    double* x,
	    double* w,
	    int& i,
	    int& ierr,
	    int& mc,
	    int& finl,
	    int& finr,
	    double* endl,
	    double* endr,
	    double* xfer,
	    double* wfer
	    // Function wf(x,i) removed for porting. Up to the user to implement it.
	    );

  void radau(int& n,
	     float* alpha,
	     float* beta,
	     float& end,
	     float* zero,
	     float* weight,
	     int& ierr,
	     float* e, // dim n+2
	     float* a, // dim n+2
	     float* b // dim n+2
	     );
  void dradau(int& n,
	      double* alpha,
	      double* beta,
	      double& end,
	      double* zero,
	      double* weight,
	      int& ierr,
	      double* e, // dim n+2
	      double* a, // dim n+2
	      double* b // dim n+2
	      );

  void recur(int& n,
	     int& ipoly, 
	     float& al,
	     float& be,
	     float* a, 
	     float* b, 
	     int& ierr);
  void drecur(int& n, 
	      int& ipoly, 
	      double& al, 
	      double& be, 
	      double* a, 
	      double* b, 
	      int& ierr);

  void sti(int& n,
	   int& ncap,
	   float* x,
	   float* w,
	   float* alpha,
	   float* beta,
	   int& ierr,
	   float* p0,
	   float* p1,
	   float* p2);
  void dsti(int& n,
	    int& ncap,
	    double* x,
	    double* w,
	    double* alpha,
	    double* beta,
	    int& ierr,
	    double* p0,
	    double* p1,
	    double* p2);
}

#endif
