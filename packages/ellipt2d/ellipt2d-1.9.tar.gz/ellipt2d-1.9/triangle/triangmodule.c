/* $Id: triangmodule.c,v 1.16 2005/11/08 13:15:56 pletzer Exp $ */

/* this appears to be necessary to run on Linux */

#if defined(Py_DEBUG) || defined(DEBUG)
extern void _Py_CountReferences(FILE*);
#define CURIOUS(x) { fprintf(stderr, __FILE__ ":%d ", __LINE__); x; }
#else
#define CURIOUS(x)
#endif
#define MARKER()        CURIOUS(fprintf(stderr, "\n"))
#define DESCRIBE(x)     CURIOUS(fprintf(stderr, "  " #x "=%d\n", x))
#define DESCRIBE_HEX(x) CURIOUS(fprintf(stderr, "  " #x "=%08x\n", x))
#define COUNTREFS()     CURIOUS(_Py_CountReferences(stderr))

#undef _STDLIB_H_
#define _STDLIB_H_


/*  This code interfaces ellipt2d directly with "triangle", a general        
    purpose triangulation code. In doing so, Python data structures          
    are passed to C for  use by "triangle" and the results are then          
    converted back. This was accomplished using the Python/C API.            
                                                                           
    I. Lists of points,edges,holes, and regions must normally be 
     created for proper triangulation. However, if there are no holes,
     the edge list and hole list need not be specified (however, a 
     measure of control over the shape of the convex hull is lost; 
     triangle decides). In additon an intial area constraint for          
     triangles must be provided upon initialization of an Ireg2tri           
     object.

     points list: [(x1,y1),(x2,y2),...] (Tuples of doubles)                  
     edge list: [(Ea,Eb),(Ef,Eg),...] (Tuples of integers)                   
     hole list: [(x1,y1),...](Tuples of doubles, one inside each hole region)
     regionlist: [ (x1,y1,index,area),...] (Tuple of doubles)                

     This is all that is needed to accomplish an intial triangulation.       
     A dictionary in the form of the Node class data structure is            
     returned and passed to a Node object.                                   
                                                        
          A. To deal with Dirichlet boundary conditions a method           
     setUpDirchlet(...) is supplied. This takes a Dirichlet boundary       
     object and sets the second of four point attributes in triangle       
     to the boundary value. The first attribute is reserved for accounting 
     of unwanted interpolation of boudary values by triangle(for           
     each boundary node requiring Dirichlet boundary conditions it is      
     set to 1). After triangulation and/or refinement the method           
     updateDirichlet(...) is used to update the original dirichlet         
     Boundary object in the driver. It only returns points with            
     first attribute equal to 1 and on the boundary. Thus, using triangle  
     to deal with boudary value alterations due to added points during     
     refinement requires that BC's be specified only on a boundary and     
     not the interior of a domain. Otherwise,an update will ommit          
     non-boundary points. These points should be set afterwards.           
     (Triangle forms a smooth interpolation of sharp changes in boundary     
     values when intermediate points are added)                           
          B. Robbins (and its subset Neumann) boundary condtions are not      
     treated like the Dirichlet type(Mainly because Triangle lacks an      
     attribute list for edges). Users must employ the setAttributes(...)   
     and getAttributes(...) methods. These are specified using the         
     third and fourth point attributes. They may be used as seen fit.      
                                                                           
    II.Refinement of a mesh is accomplished by storing the original          
    output in a global variable(struct triangulateio out;). When the         
    refinement routine is called, a new area parameter is passed to the      
    triagulaton routine, as well as the 'r' switch to denote refinement.     
    A new mesh is returned in the triagulateio struct next, then the         
    memory for the old output is released and out is made to point to        
    the data of next.                                                        
                    
    Since out is global, the user can be dealing with only one mesh at a     
    time. However, multiple meshes can be used if  everything that needs     
    to be accomplished with a previous mesh is already done. Out will        
    simply point to the new mesh.                                            


    Compilation can be done as follows                                       
                    
    c++ -I/usr/local/include/python1.5 -shared -o triangmodule.so            
    triangmodule.c triangle.o                                                */


#ifdef SINGLE  
#define REAL float 
#else  
#define REAL double 
#endif  

#include "triangle.h" 

#ifndef _STDLIB_H_ 
#ifndef _WIN32
extern "C" void *malloc(); 
extern "C" void free(); 
#endif
#endif  

#include "Python.h" 

struct triangulateio in,out;

#define NATTRIBUTES_DIRICHLET 2

int NATTRIBUTES_OTHER = 4;

  static PyObject *triang_setUpConvexHull(PyObject *self, PyObject *args){
     
     PyObject *hull;
     PyObject *seglist;
     PyObject *holelist;
     PyObject *regionlist;
     int  num_points, i, j, k, nattr;
     int a,b;
     int index = 0;
     double x,y;
     PyObject *pair;
     
     if(!PyArg_ParseTuple(args,(char *)"OOOOi",&hull,&seglist,&holelist,&regionlist, &NATTRIBUTES_OTHER)){
       return NULL;
     }
     if(!PyList_Check(hull)){
       PyErr_SetString(PyExc_TypeError, 
		       "incorrect first argument for 'setUpConvexHull': list required.");
       return NULL;
     }
     if(!PyList_Check(seglist)){
       PyErr_SetString(PyExc_TypeError,
		       "incorrect second argument for 'setUpConvexHull': list required.");
       return NULL;
     }
     if(!PyList_Check(holelist)){
       PyErr_SetString(PyExc_TypeError,
		       "incorrect third argument for 'setUpConvexHull': list required.");
       return NULL;
     }
     if(!PyList_Check(regionlist)){
       PyErr_SetString(PyExc_TypeError,
		       "incorrect fourth argument for 'setUpConvexHull': list required.");
       return NULL;
     }
     num_points = PyList_Size(hull);
     nattr = NATTRIBUTES_DIRICHLET+NATTRIBUTES_OTHER;
    
     /* Initialize points */
     in.numberofpoints = num_points;
     in.numberofpointattributes = nattr;
     in.pointlist = (REAL *)malloc(in.numberofpoints*2*sizeof(REAL));
     in.pointattributelist = (REAL *)malloc(in.numberofpoints*nattr*sizeof(REAL)); 
     in.pointmarkerlist = (int *)NULL; /* malloc(in.numberofpoints*sizeof(int)); */
     
     /* Initialize region fields */
/*      in.numberofregions = PyList_Size(regionlist); */
/*      in.regionlist = (REAL *)malloc(in.numberofregions*4*sizeof(REAL)); */
/*      for(i=0; i<in.numberofregions;++i){ */
/*        twoelems = PyList_GetItem(regionlist,i); */
/*        in.regionlist[4*i] = PyFloat_AsDouble(PyTuple_GetItem(twoelems,0)); */
/*        in.regionlist[4*i+1] = PyFloat_AsDouble(PyTuple_GetItem(twoelems,1)); */
/*        in.regionlist[4*i+2] = (double)i; */
/*        in.regionlist[4*i+3] = (double)1.0; */
/*      } */
     /* regionlist does not seem useful?? */
     in.numberofregions = 0;
     in.regionlist = (REAL *)NULL;
    
     /*Initialize segments */
     in.numberofsegments = PyList_Size(seglist);
     in.segmentlist = (int *)malloc(in.numberofsegments*2*sizeof(int));
     in.segmentmarkerlist = (int *)NULL; /* malloc(in.numberofsegments*sizeof(int)); */

     /*Initialize holes */
     in.numberofholes = PyList_Size(holelist);
     if (in.numberofholes != 0) {
       in.holelist = (REAL *)malloc(in.numberofholes*2*sizeof(REAL));
     } else {
       in.holelist = (REAL *)NULL;
     }

     /* Fill up segment list */
     for(i = 0; i < in.numberofsegments; ++i) {
       COUNTREFS();
       pair =  PyList_GetItem(seglist,i);
       COUNTREFS();
       a = (int)PyInt_AsLong(PyTuple_GetItem(pair,0));
       COUNTREFS();
       in.segmentlist[index] = a;
       index++;
       b = (int)PyInt_AsLong(PyTuple_GetItem(pair,1));
       COUNTREFS();
       in.segmentlist[index] = b;
       index++;
     }
     /* Fill up hole list */
     index = 0;
     for(i = 0; i < in.numberofholes; ++i) {
       pair =  PyList_GetItem(holelist,i);
       x = PyFloat_AsDouble(PyTuple_GetItem(pair,0));
       in.holelist[index] = x;
       index++;
       y = PyFloat_AsDouble(PyTuple_GetItem(pair,1));
       in.holelist[index] = y;
       index++;
     }
     /* Fill up point list */
     index = 0;
     for(i = 0; i < in.numberofpoints; ++i) {
       pair =  PyList_GetItem(hull,i);
       x = PyFloat_AsDouble(PyTuple_GetItem(pair,0));
       in.pointlist[index] = x;
       index++;
       y = PyFloat_AsDouble(PyTuple_GetItem(pair,1));
       in.pointlist[index] = y;
       index++;
     }

     /* Set to default the point attribute list */
     for(j = 0; j < in.numberofpoints; ++j){
       /* in.pointmarkerlist[j] = 0;  */
       for(k = 0; k < nattr; k++)
	 in.pointattributelist[nattr*j+k] = 0.0;
     }

     /* Fill up segment marker list w/ default values */
     /* for(j=0;j < in.numberofsegments;++j){ 
        in.segmentmarkerlist[j] = 0;
      }*/
     
    Py_INCREF(Py_None);
    return Py_None;
  }

  static PyObject *triang_setUpDirichlet(PyObject *self,PyObject *args){

    /* Places BC's in 'pointattributelist'
       (Structure of array: [a1,b1,c1,...a2,b2,c2,....]) */

    PyObject *dB;
    int index, i, nattr;
    PyObject *keys;
    nattr = NATTRIBUTES_DIRICHLET + NATTRIBUTES_OTHER;

    if(!PyArg_ParseTuple(args,(char *)"O",&dB)){
       return NULL;
    }
    if(!PyDict_Check(dB)){
      PyErr_SetString(PyExc_TypeError,
		      "Wrong argument to setUpDirichlet(...),Dictionary required.");
      return NULL;
    }

    keys = PyDict_Keys(dB);
    for(i=0;i< PyList_Size(keys);++i){
      index =(int)PyInt_AsLong(PyList_GetItem(keys,i));
      in.pointattributelist[index*nattr+NATTRIBUTES_OTHER] = PyFloat_AsDouble(PyDict_GetItem(dB,PyList_GetItem(keys,i)));
      in.pointattributelist[index*nattr+NATTRIBUTES_OTHER+1] = 1.0;
    }
    
    Py_INCREF(Py_None);
    return Py_None;
  }

  static PyObject *triang_updateDirichlet(PyObject *self,PyObject *args){

    /* updates Dirichlet boundary information after triangulation 
       and/or refinement */

    PyObject *holder = PyDict_New();
    PyObject *item, *ii;
    int i, nattr;
    nattr = NATTRIBUTES_DIRICHLET + NATTRIBUTES_OTHER;

    for(i = 0; i < out.numberofpoints; ++i){
      if( out.pointattributelist[nattr*i+NATTRIBUTES_OTHER+1] == 1.0 && out.pointmarkerlist[i] != 0 ) { 

	/*test w/ holes*/
	item = PyFloat_FromDouble(out.pointattributelist[nattr*i+NATTRIBUTES_OTHER]);
	ii = PyInt_FromLong((long)i);
	PyDict_SetItem(holder, ii, item); Py_DECREF(item); Py_DECREF(ii); 

      }
    }
    return holder;
  }
  
  static PyObject *triang_setAttributes(PyObject *self,PyObject *args){

    PyObject *attribs, *item, *elem;
    int i, j, nattr;
    nattr = NATTRIBUTES_DIRICHLET + NATTRIBUTES_OTHER;

    if(!PyArg_ParseTuple(args,(char *)"O",&attribs)){
      return NULL;
    }
    if(!PySequence_Check(attribs)){
      PyErr_SetString(PyExc_TypeError,
		      "Bad argument to setAttributes(...), sequence required.");
      return NULL;
    }

    if (NATTRIBUTES_OTHER==1){
      /* attribs is a list [a1, a2, ....] */
      for(i = 0; i < PySequence_Size(attribs); ++i){
      /* New reference */
      item = PySequence_GetItem(attribs, i);
      out.pointattributelist[nattr*i] = PyFloat_AsDouble(item);
      Py_DECREF(item);
      }
    } else {
      /* attribs is a nested list  [ [a11, a12, ...], ...]*/
      for(i = 0; i < PySequence_Size(attribs); ++i){
	item = PySequence_GetItem(attribs, i);
	for (j = 0; j <NATTRIBUTES_OTHER; ++j){
	  elem = PySequence_GetItem(item, j);
	  out.pointattributelist[nattr*i+j] = PyFloat_AsDouble(elem);
	  Py_DECREF(elem);
	}
      }
    }
    
    Py_INCREF(Py_None);
    return Py_None;
  }

  static PyObject *triang_getAttributes(PyObject *self,PyObject *args){

    PyObject *holder;
    PyObject *item;
    int i, j, nattr;
    nattr = NATTRIBUTES_DIRICHLET + NATTRIBUTES_OTHER;
    
    holder = PyList_New(out.numberofpoints);

    if (NATTRIBUTES_OTHER==1){
      /* attribs is a list [a1, a2, ....] */
      for(i = 0; i < out.numberofpoints; ++i){
	item = PyFloat_FromDouble(out.pointattributelist[nattr*i]);
	PyList_SET_ITEM(holder, i, item); /* Py_DECREF(item); */
      }
    } else {
      /* attribs is a nested list  [ [a11, a12, ...], ...]*/
      for(i = 0; i < out.numberofpoints; ++i){
	PyObject *list = PyList_New(NATTRIBUTES_OTHER);
	for(j = 0; j < NATTRIBUTES_OTHER; ++j){
	  item = PyFloat_FromDouble(out.pointattributelist[nattr*i+j]);
	  PyList_SET_ITEM(list, j, item); /* Py_DECREF(item); */
	}
	PyList_SET_ITEM(holder, i, list);
	/* Py_DECREF(list); */
      }
    }

    /* clean up */

    return holder;
  }

  static PyObject *triang_triangulate(PyObject *self, PyObject *args){
    /* triangulation routine called by Ireg2tri class to fill a node object */
    
     PyObject *mode;
     int i;
     char *mod;
     long k,l;
     PyObject *mtemp;
     PyObject *contemp;
     PyObject *kk, *ll;
     PyObject *holder;


     if(!PyArg_ParseTuple(args,(char *)"O",&mode)){ 
       return NULL; 
     } 

     /* set up the switch arguments to the triangulation routine */

     mod = PyString_AS_STRING(mode);
    
     out.pointlist = (REAL *)NULL;
     out.pointmarkerlist = (int *)NULL;
     out.numberofpointattributes = in.numberofpointattributes;
     out.pointattributelist = (REAL *)NULL;
  
     out.trianglelist = (int *)NULL;
     out.triangleattributelist = (REAL *)NULL;                   
     out.trianglearealist = (REAL *)NULL;                        
     out.neighborlist = (int *)NULL;
     
     out.segmentlist = (int *)NULL;
     out.segmentmarkerlist = (int *)NULL;
     
     out.edgelist = (int *)NULL;
     out.edgemarkerlist = (int *)NULL;
     
     out.holelist = (REAL *)NULL;
     out.regionlist = (REAL *)NULL;
    
     printf("\n\nTriangulate input args: %s \n\n", mod);
     triangulate(mod, &in, &out, (struct triangulateio *)NULL );

     /*
       ------- Pass point numbers,coordinates and neighbors back to Python ------
       we send back a dictionary:                                               
       { index : [ coordinates, [connections], Attribute ] } 
     */
     
     holder = PyDict_New();

     for(i=0; i< out.numberofpoints;++i){

       PyObject *mlist = Py_BuildValue((char *)"[(d,d),[],i]", 
	 out.pointlist[i*2  ], out.pointlist[i*2+1], out.pointmarkerlist[i]);   

       PyObject *ii = PyInt_FromLong((long)i);
       PyDict_SetItem(holder, ii, mlist); Py_DECREF(ii);

       Py_DECREF(mlist);
     }

     for(i=0;i < out.numberofedges;++i){
       k = out.edgelist[i*2];
       l = out.edgelist[i*2+1];
       
       kk = PyInt_FromLong(k);
       ll = PyInt_FromLong(l);

       mtemp = PyDict_GetItem(holder, kk);
       contemp = PyList_GetItem(mtemp,1);
       PyList_Append(contemp, ll);
       
       mtemp = PyDict_GetItem(holder, ll);
       contemp = PyList_GetItem(mtemp,1);
       PyList_Append(contemp, kk);

       Py_DECREF(kk);
       Py_DECREF(ll);
     }
     
     /* Free useless memory */
     
     return holder;
  }

  
  static PyObject *triang_refine(PyObject *self, PyObject *args){

    /* refinement routine called by Ireg2tri class */

    PyObject *mode;
    int i;
    char *mod;
    long k,l;
    struct triangulateio next;
    PyObject *mtemp;
    PyObject *contemp;
    PyObject *kk, *ll;
    PyObject *holder;

     if(!PyArg_ParseTuple(args,(char *)"O", &mode)){ 
       return NULL; 
     } 
  
    mod = PyString_AS_STRING(mode);
    
    next.pointlist = (REAL *)NULL;
    next.pointmarkerlist = (int *)NULL;
    next.numberofpointattributes = out.numberofpointattributes;
    next.pointattributelist = (REAL *)NULL;
    next.trianglelist = (int *)NULL;
    next.triangleattributelist = (REAL *)NULL;                  
    next.trianglearealist = (REAL *)NULL;                       
    next.neighborlist = (int *)NULL;
    next.segmentlist = (int *)NULL;
    next.segmentmarkerlist = (int *)NULL;
    next.edgelist = (int *)NULL;
    next.edgemarkerlist = (int *)NULL;
    next.holelist = (REAL *)NULL;
    next.regionlist = (REAL *)NULL;

    printf("\n\n Refine input arguments %s \n\n", mod);
    triangulate(mod ,&out,&next,(struct triangulateio *)NULL );

    if(out.pointlist){
      free(out.pointlist);  
      out.pointlist = NULL;
    }
    if(out.pointmarkerlist){
      free(out.pointmarkerlist);  
      out.pointmarkerlist = NULL;
    }
    if(out.pointattributelist){
      free(out.pointattributelist);  
      out.pointattributelist = NULL;
    }
    if(out.trianglelist){
      free(out.trianglelist);  
      out.trianglelist = NULL;
    }
    if(out.triangleattributelist){
      free(out.triangleattributelist);  
      out.triangleattributelist = NULL;
    }
    if(out.trianglearealist){
      free(out.trianglearealist);  
      out.trianglearealist = NULL;
    }
    if(out.neighborlist){
      free(out.neighborlist);  
      out.neighborlist = NULL;
    }
    if(out.segmentlist){
      free(out.segmentlist);    
      out.segmentlist = NULL;
    }
    if(out.normlist){
      free(out.segmentmarkerlist);   
      out.segmentmarkerlist = NULL;
    } 
    if(out.edgelist){
      free(out.edgelist);    
      out.edgelist = NULL;
    }
    if(out.edgemarkerlist){
      free(out.edgemarkerlist);   
      out.edgemarkerlist = NULL;
    }
    /* free(out.holelist);  out.holelist = NULL; */
    /* free(out.regionlist);  out.regionlist = NULL; */
/*     if(out.normlist){ */
/*       free(out.normlist);  */
/*       out.normlist = NULL; */
/*     } */

    out = next;

    holder = PyDict_New();

    for(i=0; i< out.numberofpoints;++i){
      PyObject *mlist = Py_BuildValue((char *)"[(d,d),[],i]", 
	  out.pointlist[i*2  ],  out.pointlist[i*2+1], out.pointmarkerlist[i]);

      PyObject *ii = PyInt_FromLong((long)i);
      PyDict_SetItem(holder, ii, mlist); Py_DECREF(ii);

      Py_DECREF(mlist);
    }

    for(i=0;i < out.numberofedges;++i){
      k = out.edgelist[i*2]; 
      l = out.edgelist[i*2+1];
      kk = PyInt_FromLong(k);
      ll = PyInt_FromLong(l);

      mtemp = PyDict_GetItem(holder, kk);
      contemp = PyList_GetItem(mtemp,1);
      PyList_Append(contemp, ll);
       
      mtemp = PyDict_GetItem(holder, ll);
      contemp = PyList_GetItem(mtemp,1);
      PyList_Append(contemp, kk); 

      Py_DECREF(kk);
      Py_DECREF(ll);
    }
     
    /* Clean up */

    return holder;    
  }

  static PyObject* triang_delete(PyObject *self, PyObject *args){

    /* OUT */

    if(out.pointlist){
      free(out.pointlist);  out.pointlist=NULL;
    }
    if(out.pointmarkerlist){    
      free(out.pointmarkerlist); out.pointmarkerlist=NULL;
    }
    if(out.pointattributelist){    
      free(out.pointattributelist); out.pointattributelist=NULL;
    }
    if(out.trianglelist){    
      free(out.trianglelist); out.trianglelist=NULL;
    }
    if(out.triangleattributelist){    
      free(out.triangleattributelist); out.triangleattributelist=NULL;
    }
    if(out.trianglearealist){    
      free(out.trianglearealist); out.trianglearealist=NULL;
    }
    if(out.neighborlist){    
      free(out.neighborlist); out.neighborlist=NULL;
    }
    if(out.segmentlist){
      free(out.segmentlist); out.segmentlist =NULL;
    }
    if(out.segmentmarkerlist){
      free(out.segmentmarkerlist); out.segmentmarkerlist  =NULL;
    }
    if(out.edgelist){
      free(out.edgelist);  out.edgelist=NULL;
    }
    if(out.edgemarkerlist){
      free(out.edgemarkerlist);  out.edgemarkerlist=NULL;
    }
    /* references to corresponding in members */
/*     if(out.holelist){ */
/*       free(out.holelist); out.holelist=NULL; */
/*     } */
/*     if(out.regionlist){ */
/*       free(out.regionlist); out.regionlist=NULL; */
/*     } */
/*     if(out.normlist){ */
/*       free(out.normlist); out.normlist=NULL; */
/*     } */
    
    /*  IN */

    if(in.pointlist){
      free(in.pointlist);  in.pointlist   =NULL;             
    }
    if(in.pointattributelist){
      free(in.pointattributelist); in.pointattributelist =NULL;       
    }
    if(in.pointmarkerlist){
      free(in.pointmarkerlist); in.pointmarkerlist    =NULL;        
    }
    if(in.segmentlist){
      free(in.segmentlist);  in.segmentlist    =NULL;         
    }
    if(in.segmentmarkerlist){
      free(in.segmentmarkerlist); in.segmentmarkerlist    =NULL;   
    }
    if(in.regionlist){
      free(in.regionlist); in.regionlist  =NULL;            
    }
    if(in.holelist){
      free(in.holelist); in.holelist=NULL;
    }
   
    Py_INCREF(Py_None);
    return Py_None;
  }

  static PyMethodDef triang_methods[] = {
    {(char *)"triangulate", triang_triangulate, 1 ,(char *)"Uses triangle to generate an unstructured mesh.(<PyString area>,<PyString mode>)-> Node object's data strucutre."},
    {(char *)"refine", triang_refine, 1, (char *)"Refines a previously generated mesh.(<PyString area>,<PyString mode>)-> Node object's data structure."},
    {(char *)"setUpConvexHull", triang_setUpConvexHull, 1, (char *)"Passes hull points to triangle.All arguments are lists.(<hull>,<seglist>,<holelist>,<regionlist>)-><hull>"},
    {(char *)"setUpDirichlet", triang_setUpDirichlet, 1, (char *)"Uses dirchlet boundary object to set point attributes in triangle.(<dB dictionary data strucuture>)-><dB>"},
    {(char *)"updateDirichlet", triang_updateDirichlet, 1, (char *)"Returns updated boundary value information(post triangulation),()-><dB dictionary data structure>"},
    {(char *)"setAttributes", triang_setAttributes, 1, (char *)"Directly sets point attributes,(<Dict of point attribtes>)-><Dictionary of point attributes>" },
    {(char *)"getAttributes", triang_getAttributes, 1, (char *)"Gets point attributes,()-><Dictionary of point attributes>"},
    {(char *)"delete", triang_delete, 1, (char *)"Frees memory allocated by triangle,()->Py_None"},
    {NULL,NULL}
  };

  void inittriang(){
    Py_InitModule((char *)"triang",triang_methods);
  }














































































