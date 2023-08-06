#ifndef __PYX_HAVE__cypari__gen
#define __PYX_HAVE__cypari__gen


#ifndef __PYX_HAVE_API__cypari__gen

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(void) set_pari_signals(void);
__PYX_EXTERN_C DL_IMPORT(void) unset_pari_signals(void);

__PYX_EXTERN_C DL_IMPORT(jmp_buf) jmp_env;

#endif /* !__PYX_HAVE_API__cypari__gen */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initgen(void);
#else
PyMODINIT_FUNC PyInit_gen(void);
#endif

#endif /* !__PYX_HAVE__cypari__gen */
