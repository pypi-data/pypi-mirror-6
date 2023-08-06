#include <src/ORTHPOLPP.hpp>

extern "C"
{
  void quad_(int& n, float* x, float* w, int& i, int& ierr);
  void dquad_(int& n, double* x, double* w, int& i, int& ierr);
  float wf_(float& x, int& i);
  double dwf_(double& x, int& i);
}

void (*quad_callback)(int& n, float* x, float* w, int& i, int& ierr);
void (*dquad_callback)(int& n, double* x, double* w, int& i, int& ierr);
float (*wf_callback)(float& x, int& i);
double (*dwf_callback)(double& x, int& i);

void quad_(int& n, float* x, float* w, int& i, int& ierr){
  quad_callback(n , x, w, i, ierr);
}

void dquad_(int& n, double* x, double* w, int& i, int& ierr){
  dquad_callback(n , x, w, i, ierr);
}

float wf_(float& x, int& i){
  return wf_callback(x, i);
}

double dwf_(double& x, int& i){
  return dwf_callback(x, i);
}

namespace orthpol
{
  void set_quad_callback(void (*pointer)(int& n, float* x, float* w, int& i, int& ierr)){
    quad_callback = pointer;
  }

  void set_dquad_callback(void (*pointer)(int& n, double* x, double* w, int& i, int& ierr)){
    dquad_callback = pointer;
  }

  void set_wf_callback(float (*pointer)(float& x, int& i)){
    wf_callback = pointer;
  }

  void set_dwf_callback(double (*pointer)(double& x, int& i)){
    dwf_callback = pointer;
  }

  float r1mach(int& I){
    return r1mach_(I);
  }

  double d1mach(int& I){
    return d1mach_(I);
  }

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
	    float* s2){
    cheb_(n, a, b, fnu, alpha, beta, s, ierr, s0, s1, s2);
  }

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
	     double* s2){
    dcheb_(n, a, b, fnu, alpha, beta, s, ierr, s0, s1, s2);
  }

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
	    int& ierr){
    chri_(n, iopt, a, b, x, y, hr, hi, alpha, beta, ierr);
  }

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
	     int& ierr){
    dchri_(n, iopt, a, b, x, y, hr, hi, alpha, beta, ierr);
  }

  void gauss(int& n,
	     float* alpha,
	     float* beta,
	     float& eps,
	     float* zero,
	     float* weight,
	     int& ierr,
	     float* e){
    gauss_(n, alpha, beta, eps, zero, weight, ierr, e);
  }

  void dgauss(int& n,
	      double* alpha,
	      double* beta,
	      double& eps,
	      double* zero,
	      double* weight,
	      int& ierr,
	      double* e){
    dgauss_(n, alpha, beta, eps, zero, weight, ierr, e);
  }

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
	     ){
    gchri_(n,
	   iopt,
	   nu0,
	   numax,
	   eps,
	   a,
	   b,
	   x,
	   y,
	   alpha,
	   beta,
	   nu,
	   ierr,
	   ierrc, // inherited error flag from cheb
	   fnu, // dim 2*n
	   s,   // dim n
	   s0,  // dim 2*n
	   s1,  // dim 2*n
	   s2 // dim 2*n
	   );
  }

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
	      ){
    dgchri_(n,
	    iopt,
	    nu0,
	    numax,
	    eps,
	    a,
	    b,
	    x,
	    y,
	    alpha,
	    beta,
	    nu,
	    ierr,
	    ierrc, // inherited error flag from cheb
	    fnu, // dim 2*n
	    s,   // dim n
	    s0,  // dim 2*n
	    s1,  // dim 2*n
	    s2 // dim 2*n
	    );
  }

  void lancz(int &n,
	     int& ncap,
	     float* x,
	     float* w,
	     float* alpha,
	     float* beta,
	     int& ierr,
	     float* p0,
	     float* p1){
    lancz_(n,
	   ncap,
	   x,
	   w,
	   alpha,
	   beta,
	   ierr,
	   p0,
	   p1);
  }

  void dlancz(int &n,
	      int& ncap,
	      double* x,
	      double* w,
	      double* alpha,
	      double* beta,
	      int& ierr,
	      double* p0,
	      double* p1){
    dlancz_(n,
	    ncap,
	    x,
	    w,
	    alpha,
	    beta,
	    ierr,
	    p0,
	    p1);
  }

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
	   ){
    lob_( n,
	  alpha,
	  beta,
	  aleft,
	  right,
	  zero,
	  weight,
	  ierr,
	  e,  // dim n+2
	  a,  // dim n+2
	  b   // dim n+2
	  );
  }

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
	    ){
    dlob_( n,
	   alpha,
	   beta,
	   aleft,
	   right,
	   zero,
	   weight,
	   ierr,
	   e,  // dim n+2
	   a,  // dim n+2
	   b   // dim n+2
	   );
  }

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
	      ){
    mccheb_( n,
	     ncapm,
	     mc,
	     mp,
	     xp, // dim mp
	     yp, // dim mp
	     // function quad is removed and up to the user to be implemented
	     eps,
	     iq,
	     idelta,
	     finl, // Needed by qgp (logical)
	     finr, // Needed by qgp (logical)
	     endl, // Needed by qgp
	     endr, // Needed by qgp
	     xfer, // Needed by qgp
	     wfer, // Needed by qgp
	     a,
	     b,
	     fnu,
	     alpha, // dim n
	     beta, // dim n
	     ncap,
	     kount,
	     ierr,
	     be, // dimension n
	     x, // dim ncapm
	     w, // dim ncapm
	     xm, // dim mc*ncapm+mp
	     wm, // dim mc*ncapm+mp
	     s, // dim mc*ncapm+mp ?
	     s0, // dim mc*ncapm+mp ?
	     s1, // dim mc*ncapm+mp ?
	     s2 // dim mc*ncapm+mp  ?
	     );
  }

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
	      ){
    dmcheb_( n,
	     ncapm,
	     mc,
	     mp,
	     xp, // dim mp
	     yp, // dim mp
	     // function quad is removed and up to the user to be implemented
	     eps,
	     iq,
	     idelta,
	     finl, // Needed by qgp (logical)
	     finr, // Needed by qgp (logical)
	     endl, // Needed by qgp
	     endr, // Needed by qgp
	     xfer, // Needed by qgp
	     wfer, // Needed by qgp
	     a,
	     b,
	     fnu,
	     alpha, // dim n
	     beta, // dim n
	     ncap,
	     kount,
	     ierr,
	     be, // dimension n
	     x, // dim ncapm
	     w, // dim ncapm
	     xm, // dim mc*ncapm+mp
	     wm, // dim mc*ncapm+mp
	     s, // dim mc*ncapm+mp ?
	     s0, // dim mc*ncapm+mp ?
	     s1, // dim mc*ncapm+mp ?
	     s2 // dim mc*ncapm+mp  ?
	     );
  }

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
	     ){
    mcdis_(n,
	   ncapm,
	   mc,
	   mp,
	   xp, // dim mp
	   yp, // dim mp
	   // function quad is removed and up to the user to be implemented
	   eps,
	   iq,
	   idelta,
	   irout,
	   finl, // Needed by qgp (logical)
	   finr, // Needed by qgp (logical)
	   endl, // Needed by qgp
	   endr, // Needed by qgp
	   xfer, // Needed by qgp
	   wfer, // Needed by qgp
	   alpha, // dim n
	   beta, // dim n
	   ncap,
	   kount,
	   ierr,
	   ie,
	   be, // dimension n
	   x, // dim ncapm
	   w, // dim ncapm
	   xm, // dim mc*ncapm+mp
	   wm, // dim mc*ncapm+mp
	   p0, // dim mc*ncapm+mp
	   p1, // dim mc*ncapm+mp
	   p2 // dim mc*ncapm+mp
	   );
  }

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
	      ){
    dmcdis_(n,
	    ncapm,
	    mc,
	    mp,
	    xp, // dim mp
	    yp, // dim mp
	    // function quad is removed and up to the user to be implemented
	    eps,
	    iq,
	    idelta,
	    irout,
	    finl, // Needed by qgp (logical)
	    finr, // Needed by qgp (logical)
	    endl, // Needed by qgp
	    endr, // Needed by qgp
	    xfer, // Needed by qgp
	    wfer, // Needed by qgp
	    alpha, // dim n
	    beta, // dim n
	    ncap,
	    kount,
	    ierr,
	    ie,
	    be, // dimension n
	    x, // dim ncapm
	    w, // dim ncapm
	    xm, // dim mc*ncapm+mp
	    wm, // dim mc*ncapm+mp
	    p0, // dim mc*ncapm+mp
	    p1, // dim mc*ncapm+mp
	    p2 // dim mc*ncapm+mp
	    );
  }

  void nu0her(int& n,
	      COMPLEX<double>& z,
	      double& eps){
    nu0her_(n, z, eps);
  }

  void nu0jac(int& n,
	      COMPLEX<double>& z,
	      double& eps){
    nu0jac_(n, z, eps);
  }

  void nu0lag(int& n,
	      COMPLEX<double>& z,
	      double& eps){
    nu0lag_(n, z, eps);
  }

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
	   ){
    qgp_( n,
	  x,
	  w,
	  i,
	  ierr,
	  mc,
	  finl,
	  finr,
	  endl,
	  endr,
	  xfer,
	  wfer
	  // Function wf(x,i) removed for porting. Up to the user to implement it.
	  );
  }

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
	    ){
    dqgp_( n,
	   x,
	   w,
	   i,
	   ierr,
	   mc,
	   finl,
	   finr,
	   endl,
	   endr,
	   xfer,
	   wfer
	   // Function wf(x,i) removed for porting. Up to the user to implement it.
	   );
  }

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
	     ){
    radau_( n,
	    alpha,
	    beta,
	    end,
	    zero,
	    weight,
	    ierr,
	    e, // dim n+2
	    a, // dim n+2
	    b // dim n+2
	    );
  }

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
	      ){
    dradau_( n,
	     alpha,
	     beta,
	     end,
	     zero,
	     weight,
	     ierr,
	     e, // dim n+2
	     a, // dim n+2
	     b // dim n+2
	     );
  }

  void recur(int& n,
	     int& ipoly, 
	     float& al,
	     float& be,
	     float* a, 
	     float* b, 
	     int& ierr){
    recur_( n,
	    ipoly, 
	    al,
	    be,
	    a, 
	    b, 
	    ierr);
  }

  void drecur(int& n, 
	      int& ipoly, 
	      double& al, 
	      double& be, 
	      double* a, 
	      double* b, 
	      int& ierr){
    drecur_( n,
	     ipoly, 
	     al,
	     be,
	     a, 
	     b, 
	     ierr);
  }

  void sti(int& n,
	   int& ncap,
	   float* x,
	   float* w,
	   float* alpha,
	   float* beta,
	   int& ierr,
	   float* p0,
	   float* p1,
	   float* p2){
    sti_( n,
	  ncap,
	  x,
	  w,
	  alpha,
	  beta,
	  ierr,
	  p0,
	  p1,
	  p2);
  }

  void dsti(int& n,
	    int& ncap,
	    double* x,
	    double* w,
	    double* alpha,
	    double* beta,
	    int& ierr,
	    double* p0,
	    double* p1,
	    double* p2){
    dsti_( n,
	   ncap,
	   x,
	   w,
	   alpha,
	   beta,
	   ierr,
	   p0,
	   p1,
	   p2);
  }

}
